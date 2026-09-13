<?xml version='1.0' encoding='utf-8'?>
<q:quakeml xmlns="http://quakeml.org/xmlns/bed/1.2" xmlns:q="http://quakeml.org/xmlns/quakeml/1.2">
  <eventParameters publicID="smi:org.gfz-potsdam.de/geofon/EventParameters">
    <event publicID="smi:org.gfz-potsdam.de/geofon/texnet2021ynzp">
      <preferredOriginID>smi:org.gfz-potsdam.de/geofon/NLL.20211216173259.674009.98808</preferredOriginID>
      <preferredMagnitudeID>smi:org.gfz-potsdam.de/geofon/Magnitude/20211216173818.404861.99308</preferredMagnitudeID>
      <type>earthquake</type>
      <typeCertainty>known</typeCertainty>
      <description>
        <text>Western Texas</text>
        <type>region name</type>
      </description>
      <creationInfo>
        <agencyID>TXNet</agencyID>
        <author>scevent@sc3primary.beg.utexas.edu</author>
        <creationTime>2021-12-16T04:33:40.336180Z</creationTime>
      </creationInfo>
      <origin publicID="smi:org.gfz-potsdam.de/geofon/NLL.20211216173259.674009.98808">
        <time>
          <value>2021-12-16T04:33:27.070523Z</value>
        </time>
        <latitude>
          <value>32.06451416</value>
          <uncertainty>0.2643621015</uncertainty>
        </latitude>
        <longitude>
          <value>-102.2393054</value>
          <uncertainty>0.2237453721</uncertainty>
        </longitude>
        <depth>
          <value>10344.36035</value>
          <uncertainty>717.5626679</uncertainty>
        </depth>
        <methodID>smi:org.gfz-potsdam.de/geofon/NonLinLoc</methodID>
        <earthModelID>smi:org.gfz-potsdam.de/geofon/iasp91</earthModelID>
        <quality>
          <associatedPhaseCount>77</associatedPhaseCount>
          <usedPhaseCount>45</usedPhaseCount>
          <usedStationCount>27</usedStationCount>
          <standardError>0.1379858507</standardError>
          <azimuthalGap>57.48979391</azimuthalGap>
          <secondaryAzimuthalGap>57.48979391</secondaryAzimuthalGap>
          <groundTruthLevel>-</groundTruthLevel>
          <minimumDistance>0.0649617466</minimumDistance>
          <maximumDistance>0.9308552688</maximumDistance>
          <medianDistance>0.4287398214</medianDistance>
        </quality>
        <evaluationMode>manual</evaluationMode>
        <evaluationStatus>final</evaluationStatus>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:33:04.560990Z</creationTime>
        </creationInfo>
        <originUncertainty>
          <horizontalUncertainty>418.7080854</horizontalUncertainty>
          <minHorizontalUncertainty>317.1229374</minHorizontalUncertainty>
          <maxHorizontalUncertainty>418.7080854</maxHorizontalUncertainty>
          <azimuthMaxHorizontalUncertainty>153.7952642</azimuthMaxHorizontalUncertainty>
          <confidenceEllipsoid>
            <semiMajorAxisLength>1366806.695</semiMajorAxisLength>
            <semiMinorAxisLength>345457.2982</semiMinorAxisLength>
            <semiIntermediateAxisLength>503491.1216</semiIntermediateAxisLength>
            <majorAxisPlunge>9.884385299</majorAxisPlunge>
            <majorAxisAzimuth>-113.4840917</majorAxisAzimuth>
            <majorAxisRotation>81.40385507</majorAxisRotation>
          </confidenceEllipsoid>
        </originUncertainty>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702514.66640_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702514.66640</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>190.1293612</azimuth>
          <distance>0.0649617466</distance>
          <timeResidual>-0.3980838634</timeResidual>
          <timeWeight>0.4316541315</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702546.66641_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702546.66641</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>43.23891475</azimuth>
          <distance>0.08955741852</distance>
          <timeResidual>-0.04489082001</timeResidual>
          <timeWeight>1.425263775</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702568.66642_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702568.66642</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>43.23891475</azimuth>
          <distance>0.08955741852</distance>
          <timeResidual>-0.0104696808</timeResidual>
          <timeWeight>1.44973255</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702594.66643_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702594.66643</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>177.0122248</azimuth>
          <distance>0.1157358997</distance>
          <timeResidual>-0.07386409851</timeResidual>
          <timeWeight>1.372703604</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702616.66644_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702616.66644</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>177.0122248</azimuth>
          <distance>0.1157358997</distance>
          <timeResidual>-0.1027215577</timeResidual>
          <timeWeight>1.296680116</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702645.66645_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702645.66645</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>213.1125761</azimuth>
          <distance>0.1313846344</distance>
          <timeResidual>-0.01981706238</timeResidual>
          <timeWeight>1.447484706</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702669.66646_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702669.66646</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>213.1125761</azimuth>
          <distance>0.1313846344</distance>
          <timeResidual>0.02686313899</timeResidual>
          <timeWeight>1.41898322</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702697.66647_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702697.66647</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>203.3782568</azimuth>
          <distance>0.1412667997</distance>
          <timeResidual>-0.002260211089</timeResidual>
          <timeWeight>1.448911165</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702721.66648_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702721.66648</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>203.3782568</azimuth>
          <distance>0.1412667997</distance>
          <timeResidual>0.06333021536</timeResidual>
          <timeWeight>1.340448997</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70275.66649_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70275.66649</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>217.1259818</azimuth>
          <distance>0.169611117</distance>
          <timeResidual>0.01715273128</timeResidual>
          <timeWeight>1.436465316</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702774.66650_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702774.66650</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>217.1259818</azimuth>
          <distance>0.169611117</distance>
          <timeResidual>0.116896069</timeResidual>
          <timeWeight>1.152860156</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702801.66651_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702801.66651</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>202.8856617</azimuth>
          <distance>0.1955788468</distance>
          <timeResidual>0.01468941187</timeResidual>
          <timeWeight>1.438861992</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702824.66652_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702824.66652</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>202.8856617</azimuth>
          <distance>0.1955788468</distance>
          <timeResidual>0.05739472143</timeResidual>
          <timeWeight>1.327737924</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702851.66653_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702851.66653</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>260.0288523</azimuth>
          <distance>0.2130754018</distance>
          <timeResidual>-0.01601073348</timeResidual>
          <timeWeight>1.448806085</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702874.66654_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702874.66654</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>260.0288523</azimuth>
          <distance>0.2130754018</distance>
          <timeResidual>0.01868042237</timeResidual>
          <timeWeight>1.379949201</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702903.66655_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702903.66655</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>69.91333011</azimuth>
          <distance>0.2405394806</distance>
          <timeResidual>0.06828058382</timeResidual>
          <timeWeight>1.335582451</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702927.66656_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702927.66656</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>69.91333011</azimuth>
          <distance>0.2405394806</distance>
          <timeResidual>0.1747331973</timeResidual>
          <timeWeight>0.9109782848</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702957.66657_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702957.66657</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>282.0391863</azimuth>
          <distance>0.268452419</distance>
          <timeResidual>0.01959760651</timeResidual>
          <timeWeight>1.425984189</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702982.66658_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702982.66658</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>282.0391863</azimuth>
          <distance>0.268452419</distance>
          <timeResidual>0.03788608578</timeResidual>
          <timeWeight>1.315321454</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703009.66659_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703009.66659</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>58.24935654</azimuth>
          <distance>0.3465519072</distance>
          <timeResidual>0.07000987554</timeResidual>
          <timeWeight>1.301795093</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703031.66660_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703031.66660</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>58.24935654</azimuth>
          <distance>0.3465519072</distance>
          <timeResidual>-0.01239182206</timeResidual>
          <timeWeight>1.056310185</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703059.66661_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703059.66661</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>102.9593436</azimuth>
          <distance>0.3826113701</distance>
          <timeResidual>-0.004081813536</timeResidual>
          <timeWeight>1.397406</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703083.66662_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703083.66662</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>102.9593436</azimuth>
          <distance>0.3826113701</distance>
          <timeResidual>-0.05718061182</timeResidual>
          <timeWeight>1.241369025</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70311.66663_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70311.66663</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>61.96933263</azimuth>
          <distance>0.4287398214</distance>
          <timeResidual>-0.04254729616</timeResidual>
          <timeWeight>1.363348042</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703137.66664_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703137.66664</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>161.4519174</azimuth>
          <distance>0.418687873</distance>
          <timeResidual>-0.06774397389</timeResidual>
          <timeWeight>1.334407235</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703161.66665_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703161.66665</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>161.4519174</azimuth>
          <distance>0.418687873</distance>
          <timeResidual>-0.2399386751</timeResidual>
          <timeWeight>0.843006714</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70319.66666_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70319.66666</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>52.15201614</azimuth>
          <distance>0.4488980928</distance>
          <timeResidual>-0.03247273072</timeResidual>
          <timeWeight>1.362507684</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703215.66667_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703215.66667</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>52.15201614</azimuth>
          <distance>0.4488980928</distance>
          <timeResidual>-0.286979</timeResidual>
          <timeWeight>0.7190698597</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703244.66668_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703244.66668</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>339.5289802</azimuth>
          <distance>0.5992878447</distance>
          <timeResidual>0.005181309929</timeResidual>
          <timeWeight>1.290116261</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703269.66669_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703269.66669</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>339.5289802</azimuth>
          <distance>0.5992878447</distance>
          <timeResidual>-0.2191081116</timeResidual>
          <timeWeight>0.8353804408</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703297.66670_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703297.66670</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>29.6091685</azimuth>
          <distance>0.6474066713</distance>
          <timeResidual>-0.2616429673</timeResidual>
          <timeWeight>0.8060493105</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703321.66671_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703321.66671</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>29.6091685</azimuth>
          <distance>0.6474066713</distance>
          <timeResidual>-0.4837931089</timeResidual>
          <timeWeight>0.4913034901</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703355.66672_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703355.66672</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>63.1359619</azimuth>
          <distance>0.8278749641</distance>
          <timeResidual>-0.7507276024</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703381.66673_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703381.66673</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>63.1359619</azimuth>
          <distance>0.8278749641</distance>
          <timeResidual>-0.5894909168</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703408.66674_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703408.66674</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>279.6029846</azimuth>
          <distance>0.8500910861</distance>
          <timeResidual>-0.4969116903</timeResidual>
          <timeWeight>0.450882991</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703435.66675_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703435.66675</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>279.6029846</azimuth>
          <distance>0.8500910861</distance>
          <timeResidual>-1.051078141</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703464.66676_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703464.66676</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>211.6571281</azimuth>
          <distance>0.8501455582</distance>
          <timeResidual>-0.8376475861</timeResidual>
          <timeWeight>0.1303366475</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703489.66677_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703489.66677</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>211.6571281</azimuth>
          <distance>0.8501455582</distance>
          <timeResidual>-1.320566293</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703516.66678_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703516.66678</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>168.7520601</azimuth>
          <distance>0.8837133836</distance>
          <timeResidual>-1.025519146</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703543.66679_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703543.66679</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>168.7520601</azimuth>
          <distance>0.8837133836</distance>
          <timeResidual>-1.510355856</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703572.66680_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703572.66680</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>243.6075891</azimuth>
          <distance>0.9308552688</distance>
          <timeResidual>-0.5988737853</timeResidual>
          <timeWeight>0.3402448225</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703597.66681_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703597.66681</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>243.6075891</azimuth>
          <distance>0.9308552688</distance>
          <timeResidual>-0.5405418725</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703629.66682_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703629.66682</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>98.74120444</azimuth>
          <distance>0.9563063426</distance>
          <timeResidual>-0.6366981471</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703654.66683_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703654.66683</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>98.74120444</azimuth>
          <distance>0.9563063426</distance>
          <timeResidual>-1.692746977</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703681.66684_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703681.66684</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>224.3090398</azimuth>
          <distance>1.006670337</distance>
          <timeResidual>-0.8288089883</timeResidual>
          <timeWeight>0.1697112376</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703705.66685_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703705.66685</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>224.3090398</azimuth>
          <distance>1.006670337</distance>
          <timeResidual>-1.14987653</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703729.66686_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703729.66686</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>286.8117837</azimuth>
          <distance>1.02349545</distance>
          <timeResidual>-0.5382086302</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703753.66687_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703753.66687</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>286.8117837</azimuth>
          <distance>1.02349545</distance>
          <timeResidual>-1.050346826</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703781.66688_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703781.66688</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>224.0975599</azimuth>
          <distance>1.05691461</distance>
          <timeResidual>-0.7003511239</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703804.66689_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703804.66689</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>224.0975599</azimuth>
          <distance>1.05691461</distance>
          <timeResidual>-1.245773742</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703831.66690_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703831.66690</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>270.743166</azimuth>
          <distance>1.150870577</distance>
          <timeResidual>-0.2887704724</timeResidual>
          <timeWeight>0.7430246603</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.860953.98069_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.860953.98069</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>190.1293612</azimuth>
          <distance>0.0649617466</distance>
          <timeResidual>-0.2560819769</timeResidual>
          <timeWeight>0.7608770649</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.861187.98070_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.861187.98070</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>61.96933263</azimuth>
          <distance>0.4287398214</distance>
          <timeResidual>-0.2944201513</timeResidual>
          <timeWeight>0.7553638925</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.861401.98071_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.861401.98071</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>270.743166</azimuth>
          <distance>1.150870577</distance>
          <timeResidual>-1.064265869</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100678.98265_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100678.98265</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>220.3712097</azimuth>
          <distance>1.150109043</distance>
          <timeResidual>-0.8196024667</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100782.98266_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100782.98266</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>220.3712097</azimuth>
          <distance>1.150109043</distance>
          <timeResidual>-1.432268892</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.10089.98267_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.10089.98267</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>31.64798549</azimuth>
          <distance>1.179839733</distance>
          <timeResidual>-1.207019429</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100932.98268_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100932.98268</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>31.64798549</azimuth>
          <distance>1.179839733</distance>
          <timeResidual>-1.766663793</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100966.98269_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100966.98269</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>217.2130391</azimuth>
          <distance>1.187954275</distance>
          <timeResidual>-0.8628288064</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100993.98270_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100993.98270</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>217.2130391</azimuth>
          <distance>1.187954275</distance>
          <timeResidual>-1.563180166</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.10103.98271_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.10103.98271</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>223.6824548</azimuth>
          <distance>1.189982802</distance>
          <timeResidual>-1.355006063</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101063.98272_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101063.98272</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>223.6824548</azimuth>
          <distance>1.189982802</distance>
          <timeResidual>-0.7221793557</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101098.98273_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101098.98273</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>229.9071815</azimuth>
          <distance>1.211029507</distance>
          <timeResidual>-0.6444195073</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101127.98274_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101127.98274</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>229.9071815</azimuth>
          <distance>1.211029507</distance>
          <timeResidual>-0.5025605912</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101167.98275_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101167.98275</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>219.9468894</azimuth>
          <distance>1.216303704</distance>
          <timeResidual>-0.7101855345</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101205.98276_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101205.98276</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>219.9468894</azimuth>
          <distance>1.216303704</distance>
          <timeResidual>-1.333369514</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101386.98277_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101386.98277</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>53.863369</azimuth>
          <distance>1.227609635</distance>
          <timeResidual>-0.7061060967</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101539.98278_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101539.98278</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>225.2581556</azimuth>
          <distance>1.241390059</distance>
          <timeResidual>-0.5697251335</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101572.98279_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101572.98279</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>225.2581556</azimuth>
          <distance>1.241390059</distance>
          <timeResidual>-1.219261529</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461521.98441_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461521.98441</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>278.618356</azimuth>
          <distance>1.403087729</distance>
          <timeResidual>0.5320608643</timeResidual>
          <timeWeight>0.3038088207</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.46189.98442_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.46189.98442</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>63.94408847</azimuth>
          <distance>1.406162697</distance>
          <timeResidual>0.05109384448</timeResidual>
          <timeWeight>0.7429293125</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461944.98443_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461944.98443</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>53.80395857</azimuth>
          <distance>1.4259795</distance>
          <timeResidual>0.1943016726</timeResidual>
          <timeWeight>0.6597356674</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461988.98444_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461988.98444</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>140.0146346</azimuth>
          <distance>1.48573899</distance>
          <timeResidual>0.8098784227</timeResidual>
          <timeWeight>0.108241441</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462018.98445_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462018.98445</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>140.0146346</azimuth>
          <distance>1.48573899</distance>
          <timeResidual>-0.08245173833</timeResidual>
          <timeWeight>0.5920162157</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462054.98446_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462054.98446</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>47.52971695</azimuth>
          <distance>1.531499259</distance>
          <timeResidual>0.4977800943</timeResidual>
          <timeWeight>0.3963485699</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462084.98447_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462084.98447</pickID>
          <phase>S</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>47.52971695</azimuth>
          <distance>1.531499259</distance>
          <timeResidual>-0.4877307918</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
        <arrival publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462143.98448_NLL.20211216173259.674009.98808">
          <pickID>smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462143.98448</pickID>
          <phase>P</phase>
          <timeCorrection>0.0</timeCorrection>
          <azimuth>51.96485691</azimuth>
          <distance>1.613649664</distance>
          <timeResidual>1.02138221</timeResidual>
          <timeWeight>0.0</timeWeight>
        </arrival>
      </origin>
      <magnitude publicID="smi:org.gfz-potsdam.de/geofon/Magnitude/20211216173818.404861.99308">
        <mag>
          <value>3.68781847</value>
          <uncertainty>0.2042402229</uncertainty>
        </mag>
        <type>ML(TexNet)</type>
        <originID>smi:org.gfz-potsdam.de/geofon/NLL.20211216173259.674009.98808</originID>
        <methodID>smi:org.gfz-potsdam.de/geofon/trimmed_mean</methodID>
        <stationCount>13</stationCount>
        <evaluationStatus>confirmed</evaluationStatus>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:39:00.615234Z</creationTime>
        </creationInfo>
      </magnitude>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702514.66640">
        <time>
          <value>2021-12-16T04:33:30.443443Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB07" locationCode="00" channelCode="HH1"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702532Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702546.66641">
        <time>
          <value>2021-12-16T04:33:29.507610Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="MID02" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702562Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702568.66642">
        <time>
          <value>2021-12-16T04:33:31.344455Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="MID02" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702583Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702594.66643">
        <time>
          <value>2021-12-16T04:33:29.847121Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="DB" stationCode="MID01" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702609Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702616.66644">
        <time>
          <value>2021-12-16T04:33:31.888544Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="DB" stationCode="MID01" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702631Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702645.66645">
        <time>
          <value>2021-12-16T04:33:30.138753Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG02" locationCode="00" channelCode="CHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702661Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702669.66646">
        <time>
          <value>2021-12-16T04:33:32.428280Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG02" locationCode="00" channelCode="CH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702684Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702697.66647">
        <time>
          <value>2021-12-16T04:33:30.312862Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG01" locationCode="00" channelCode="CHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702713Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702721.66648">
        <time>
          <value>2021-12-16T04:33:32.734721Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG01" locationCode="00" channelCode="CH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702736Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70275.66649">
        <time>
          <value>2021-12-16T04:33:30.796013Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG04" locationCode="00" channelCode="CHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702766Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702774.66650">
        <time>
          <value>2021-12-16T04:33:33.588722Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG04" locationCode="00" channelCode="CH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702789Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702801.66651">
        <time>
          <value>2021-12-16T04:33:31.235637Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB08" locationCode="01" channelCode="HNZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702816Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702824.66652">
        <time>
          <value>2021-12-16T04:33:34.292302Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB08" locationCode="01" channelCode="HN2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702839Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702851.66653">
        <time>
          <value>2021-12-16T04:33:31.509858Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG03" locationCode="00" channelCode="CHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702866Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702874.66654">
        <time>
          <value>2021-12-16T04:33:34.779956Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OG03" locationCode="00" channelCode="CH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702889Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702903.66655">
        <time>
          <value>2021-12-16T04:33:32.080063Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB11" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702918Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702927.66656">
        <time>
          <value>2021-12-16T04:33:35.774674Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB11" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702943Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702957.66657">
        <time>
          <value>2021-12-16T04:33:32.532745Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="ODSA" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702973Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.702982.66658">
        <time>
          <value>2021-12-16T04:33:36.503350Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="ODSA" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.702997Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703009.66659">
        <time>
          <value>2021-12-16T04:33:34.012668Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="MBBB1" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703025Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703031.66660">
        <time>
          <value>2021-12-16T04:33:38.920844Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="MBBB1" locationCode="00" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703045Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703059.66661">
        <time>
          <value>2021-12-16T04:33:34.607767Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB06" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703075Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703083.66662">
        <time>
          <value>2021-12-16T04:33:40.030514Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB06" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703098Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70311.66663">
        <time>
          <value>2021-12-16T04:33:35.430430Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB10" locationCode="01" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703127Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703137.66664">
        <time>
          <value>2021-12-16T04:33:35.217147Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB01" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703153Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703161.66665">
        <time>
          <value>2021-12-16T04:33:41.008694Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB01" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703177Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.70319.66666">
        <time>
          <value>2021-12-16T04:33:35.817821Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB09" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703206Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703215.66667">
        <time>
          <value>2021-12-16T04:33:41.937724Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB09" locationCode="00" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703231Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703244.66668">
        <time>
          <value>2021-12-16T04:33:38.688236Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB04" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703260Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703269.66669">
        <time>
          <value>2021-12-16T04:33:46.897800Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB04" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703284Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703297.66670">
        <time>
          <value>2021-12-16T04:33:39.332438Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB05" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703313Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703321.66671">
        <time>
          <value>2021-12-16T04:33:48.204741Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB05" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703336Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703355.66672">
        <time>
          <value>2021-12-16T04:33:42.270688Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="OP01" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703371Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703381.66673">
        <time>
          <value>2021-12-16T04:33:54.015115Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="OP01" locationCode="00" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703396Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703408.66674">
        <time>
          <value>2021-12-16T04:33:42.946929Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="SC" stationCode="JAL" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703424Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703435.66675">
        <time>
          <value>2021-12-16T04:33:54.282803Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="SC" stationCode="JAL" locationCode="00" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703450Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703464.66676">
        <time>
          <value>2021-12-16T04:33:42.607269Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MNHN" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703480Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703489.66677">
        <time>
          <value>2021-12-16T04:33:54.015116Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MNHN" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703504Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703516.66678">
        <time>
          <value>2021-12-16T04:33:43.058531Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB02" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703532Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703543.66679">
        <time>
          <value>2021-12-16T04:33:54.928400Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB02" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703558Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703572.66680">
        <time>
          <value>2021-12-16T04:33:44.383203Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB06" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703588Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703597.66681">
        <time>
          <value>2021-12-16T04:33:57.447803Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB06" locationCode="00" channelCode="HH1"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703612Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703629.66682">
        <time>
          <value>2021-12-16T04:33:44.829612Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SGCY" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703645Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703654.66683">
        <time>
          <value>2021-12-16T04:33:57.132878Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SGCY" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703669Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703681.66684">
        <time>
          <value>2021-12-16T04:33:45.586568Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB21" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703696Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703705.66685">
        <time>
          <value>2021-12-16T04:33:59.321610Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB21" locationCode="00" channelCode="HH1"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703719Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703729.66686">
        <time>
          <value>2021-12-16T04:33:46.193102Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4T" stationCode="NM01" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703744Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703753.66687">
        <time>
          <value>2021-12-16T04:33:59.967207Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4T" stationCode="NM01" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703767Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703781.66688">
        <time>
          <value>2021-12-16T04:33:46.658921Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB19" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703796Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703804.66689">
        <time>
          <value>2021-12-16T04:34:00.856723Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB19" locationCode="00" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703819Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216044602.703831.66690">
        <time>
          <value>2021-12-16T04:33:48.716284Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="SC" stationCode="PDB" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T04:46:02.703846Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.860953.98069">
        <time>
          <value>2021-12-16T04:33:28.999030Z</value>
          <lowerUncertainty>0.1000000015</lowerUncertainty>
          <upperUncertainty>0.1000000015</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB07" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:25:37.861109Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.861187.98070">
        <time>
          <value>2021-12-16T04:33:41.278491Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="MB10" locationCode="01" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:25:37.861216Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172537.861401.98071">
        <time>
          <value>2021-12-16T04:34:03.945388Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="SC" stationCode="PDB" locationCode="00" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:25:37.861437Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100678.98265">
        <time>
          <value>2021-12-16T04:33:48.172485Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="DB02" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.100764Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100782.98266">
        <time>
          <value>2021-12-16T04:34:03.554848Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="DB02" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.100803Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.10089.98267">
        <time>
          <value>2021-12-16T04:33:48.288610Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="POST" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.100914Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100932.98268">
        <time>
          <value>2021-12-16T04:34:04.098715Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="POST" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.100952Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100966.98269">
        <time>
          <value>2021-12-16T04:33:48.767468Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="DB03" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.100985Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.100993.98270">
        <time>
          <value>2021-12-16T04:34:04.541961Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4O" stationCode="DB03" channelCode="HHN"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101011Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.10103.98271">
        <time>
          <value>2021-12-16T04:34:04.810006Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB18" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101050Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101063.98272">
        <time>
          <value>2021-12-16T04:33:48.941758Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB18" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101082Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101098.98273">
        <time>
          <value>2021-12-16T04:33:49.343825Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB30" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101117Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101127.98274">
        <time>
          <value>2021-12-16T04:34:06.284253Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB30" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101145Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101167.98275">
        <time>
          <value>2021-12-16T04:33:49.352980Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB14" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101186Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101205.98276">
        <time>
          <value>2021-12-16T04:34:05.609280Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB14" locationCode="00" channelCode="HHE"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101224Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101386.98277">
        <time>
          <value>2021-12-16T04:33:49.516659Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SN08" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101511Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101539.98278">
        <time>
          <value>2021-12-16T04:33:49.842428Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB04" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101562Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172730.101572.98279">
        <time>
          <value>2021-12-16T04:34:06.464469Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="PB04" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:27:30.101590Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461521.98441">
        <time>
          <value>2021-12-16T04:33:53.166835Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="4T" stationCode="NM02" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.461765Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.46189.98442">
        <time>
          <value>2021-12-16T04:33:52.728198Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SN09" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.461923Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461944.98443">
        <time>
          <value>2021-12-16T04:33:53.143749Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SN04" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.461965Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.461988.98444">
        <time>
          <value>2021-12-16T04:33:54.580755Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OZNA" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>positive</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.462008Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462018.98445">
        <time>
          <value>2021-12-16T04:34:13.937322Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="OZNA" locationCode="00" channelCode="HH2"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.462035Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462054.98446">
        <time>
          <value>2021-12-16T04:33:54.897637Z</value>
          <lowerUncertainty>0.400000006</lowerUncertainty>
          <upperUncertainty>0.400000006</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SN07" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.462072Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462084.98447">
        <time>
          <value>2021-12-16T04:34:14.663416Z</value>
          <lowerUncertainty>0.3000000119</lowerUncertainty>
          <upperUncertainty>0.3000000119</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SN07" locationCode="00" channelCode="HH1"></waveformID>
        <phaseHint>S</phaseHint>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.462101Z</creationTime>
        </creationInfo>
      </pick>
      <pick publicID="smi:org.gfz-potsdam.de/geofon/Pick/20211216172859.462143.98448">
        <time>
          <value>2021-12-16T04:33:56.550428Z</value>
          <lowerUncertainty>0.200000003</lowerUncertainty>
          <upperUncertainty>0.200000003</upperUncertainty>
        </time>
        <waveformID networkCode="TX" stationCode="SN10" locationCode="00" channelCode="HHZ"></waveformID>
        <phaseHint>P</phaseHint>
        <polarity>negative</polarity>
        <evaluationMode>manual</evaluationMode>
        <creationInfo>
          <agencyID>TXNet</agencyID>
          <author>Tricia</author>
          <creationTime>2021-12-16T17:28:59.462178Z</creationTime>
        </creationInfo>
      </pick>
    </event>
  </eventParameters>
</q:quakeml>
