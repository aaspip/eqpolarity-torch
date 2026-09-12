from __future__ import annotations
import numpy as np

def _xyz(az_deg,to_deg):
    a=np.deg2rad(az_deg); t=np.deg2rad(to_deg)
    return np.stack((np.sin(t)*np.cos(a),np.sin(t)*np.sin(a),-np.cos(t)),axis=0)

def focal_gridsearch_chunked(sr_azimuth,takeoff,p_pol,sp_amp,dir_cos_dict,nextra,ntotal,qextra,qtotal,maxout,ncoor,
                             *,chunk_size=4096,min_ratio_trial_solutions=0.5,min_num_sp_solutions=10,rng=None):
    """Memory-bounded rewrite of SKHASH focal_gridsearch.

    Uses two/three passes over candidate mechanisms instead of allocating
    (nobs,nmc,ncoor) arrays. Acceptance equations intentionally match SKHASH.
    Peak memory becomes O(nobs*nmc*chunk_size).
    """
    if rng is None: rng=np.random.default_rng(123)
    p_pol=np.asarray(p_pol,float); sp_amp=np.asarray(sp_amp,float)
    # Azimuth and takeoff trial counts need not be identical.  In SKHASH
    # workflows without horizontal hypocentral perturbation, azimuth may have
    # one column while takeoff contains nmc columns from depth/velocity-model
    # perturbations.  NumPy broadcasts those arrays in _xyz(), so use the
    # broadcast trial count rather than sr_azimuth.shape[1] alone.
    ntrial=max(sr_azimuth.shape[1], takeoff.shape[1]); ncoor=int(ncoor)
    # Keep the largest temporary (nobs,ntrial,chunk) arrays bounded.
    nobs_work=max(1,int(max(np.count_nonzero(p_pol),np.isfinite(sp_amp).sum())))
    adaptive=max(64,int(12_000_000/max(1,nobs_work*ntrial)))
    chunk_size=max(64,min(int(chunk_size),adaptive))
    pol_ind=np.where(p_pol!=0)[0]
    xyzp=_xyz(sr_azimuth[pol_ind],takeoff[pol_ind]) if len(pol_ind) else None
    pneg=(p_pol[pol_ind]<0)
    sp_ind=np.where(np.isfinite(sp_amp))[0]
    xyzs=_xyz(sr_azimuth[sp_ind],takeoff[sp_ind]) if len(sp_ind) else None
    b1=dir_cos_dict['b1'];b2=dir_cos_dict['b2'];b3=dir_cos_dict['b3']
    ntab=180;astep=1/ntab

    def fit_chunk(lo,hi):
        if xyzp is None: return np.zeros((ntrial,hi-lo),float)
        pb1=np.tensordot(xyzp,b1[:,lo:hi],axes=[[0],[0]])
        pb3=np.tensordot(xyzp,b3[:,lo:hi],axes=[[0],[0]])
        pred=(pb1<0)!=(pb3<0)
        return np.sum((pred != pneg[:,None,None])*np.abs(p_pol[pol_ind])[:,None,None],axis=0)

    def afit_chunk(lo,hi):
        if xyzs is None: return None
        bc3=b3[:,lo:hi];bc1=b1[:,lo:hi];bc2=b2[:,lo:hi]
        pb3=np.tensordot(xyzs,bc3,axes=[[0],[0]])
        p1=xyzs[0,:,:,None]-pb3*bc3[0]
        p2=xyzs[1,:,:,None]-pb3*bc3[1]
        p3=xyzs[2,:,:,None]-pb3*bc3[2]
        plen=np.sqrt(p1*p1+p2*p2+p3*p3); plen[plen==0]=1
        p1/=plen;p2/=plen;p3/=plen
        pp1=bc1[0]*p1+bc1[1]*p2+bc1[2]*p3
        pp2=bc2[0]*p1+bc2[1]*p2+bc2[2]*p3
        ii=np.clip(np.round((pb3+1.)/astep).astype(int),0,360)
        theta=dir_cos_dict['thetable'][ii]
        ii=np.clip(np.round((pp2+1.)/astep).astype(int),0,360)
        jj=np.clip(np.round((pp1+1.)/astep).astype(int),0,360)
        phi=dir_cos_dict['phitable'][ii,jj]
        ii=np.round(phi/(np.pi*astep)).astype(int);ii[ii>(2*ntab-1)]=0
        jj=np.round(theta/(np.pi*astep)).astype(int);jj[jj>(ntab-1)]=0
        pa=dir_cos_dict['amptable'][0,jj,ii];sa=dir_cos_dict['amptable'][1,jj,ii]
        ratio=np.zeros(pa.shape);ratio[pa==0]=4.;ratio[sa==0]=-2.;nz=(pa!=0)&(sa!=0);ratio[nz]=np.log10(4.9*sa[nz]/pa[nz])
        return np.sum(np.abs(sp_amp[sp_ind][:,None,None]-ratio),axis=0)

    # Pass 1: exact per-trial minima across all candidate mechanisms.
    minfit=np.full(ntrial,np.inf); minafit=np.full(ntrial,np.inf)
    for lo in range(0,ncoor,chunk_size):
        hi=min(ncoor,lo+chunk_size); f=fit_chunk(lo,hi);minfit=np.minimum(minfit,f.min(axis=1))
        if len(sp_ind):
            a=afit_chunk(lo,hi);minafit=np.minimum(minafit,a.min(axis=1))
    qmax=np.maximum(minfit+nextra,ntotal)
    aqmax=np.maximum(minafit+qextra,qtotal) if len(sp_ind) else None

    # Pass 2: initial accepted set; also conditioned amplitude minima for SKHASH fallback.
    accepted=[]; trial_has=np.zeros(ntrial,bool); cond_min=np.full(ntrial,np.inf)
    for lo in range(0,ncoor,chunk_size):
        hi=min(ncoor,lo+chunk_size);f=fit_chunk(lo,hi); polok=f<=qmax[:,None]
        if len(sp_ind):
            a=afit_chunk(lo,hi); cond=np.where(polok,a,np.inf);cond_min=np.minimum(cond_min,cond.min(axis=1));good=polok&(a<=aqmax[:,None])
        else: good=polok
        trial_has |= np.any(good,axis=1)
        g=np.where(np.any(good,axis=0))[0]
        if len(g): accepted.append(g+lo)
    idx=np.concatenate(accepted) if accepted else np.empty(0,int)

    if len(sp_ind) and ((len(idx)<min_num_sp_solutions) or (trial_has.mean()<min_ratio_trial_solutions)):
        # Preserve SKHASH behavior: the fallback adds nextra (not qextra).
        aqmax2=np.maximum(cond_min+nextra,qtotal);accepted=[]
        for lo in range(0,ncoor,chunk_size):
            hi=min(ncoor,lo+chunk_size);f=fit_chunk(lo,hi);a=afit_chunk(lo,hi);good=(f<=qmax[:,None])&(a<=aqmax2[:,None]);g=np.where(np.any(good,axis=0))[0]
            if len(g):accepted.append(g+lo)
        idx=np.concatenate(accepted) if accepted else np.empty(0,int)
    if len(idx)>maxout: idx=rng.choice(idx,maxout,replace=False)
    return np.vstack((b3[0,idx],b3[1,idx],b3[2,idx])),np.vstack((b1[0,idx],b1[1,idx],b1[2,idx]))
