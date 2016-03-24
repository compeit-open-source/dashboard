<?php
header('Access-Control-Allow-Origin: *');

$static_path =  "../snapsounds/";

$pathsnapsounds =  "../../USERdataFOLDERwithAverySECRETname/".$_POST['str'];
$get_result_class = "awk 'NR==6{print $3}' ".$pathsnapsounds."/results_uploaded_audio.res | cut -c-1";
/*$pathsnapsounds =  "../../USERdataFOLDERwithAverySECRETname/59492717/snapsounds/";*/
$strmodel = "../../EmoRec/models/";
/*$strIA = "../../InformationAgent/php/";*/
$strWeka = "../../EmoRec/weka-3-6-11/weka.jar";


/* call praat script */
 putenv("HOME=/var/www");
 exec("/usr/bin/praat getFeatPraat2arg.praat ".$pathsnapsounds."uploaded_audio.wav ".$pathsnapsounds."uploaded_audio.feat");
 
/* add header to feature file to create arff test file */
 exec("cat ".$static_path."arff_header.txt ".$pathsnapsounds."uploaded_audio.feat >  ".$pathsnapsounds."uploaded_audio_feat.arff");
 
/* remove last character and add class */
  exec("cat ".$pathsnapsounds."uploaded_audio_feat.arff | head -c -1 > ".$pathsnapsounds."uploaded_audio_feat_noend.arff");
    exec("cat ".$pathsnapsounds."uploaded_audio_feat_noend.arff ".$static_path."some_class.txt > ".$pathsnapsounds."uploaded_audio_feat_class.arff");
 
/* classify feature file against the arousal model */
  exec("java -cp ".$strWeka." weka.classifiers.bayes.BayesNet -l ".$strmodel."model_arousal_Praat_BN_SMOTE0_IEMOCAP_ALL.model -T ".$pathsnapsounds."uploaded_audio_feat_class.arff -p 0 > ".$pathsnapsounds."results_uploaded_audio.res");
 
/* return result class */
$a = exec($get_result_class) - 2;

/* classify feature file against the valence model */
  exec("java -cp ".$strWeka." weka.classifiers.bayes.BayesNet -l ".$strmodel."model_valence_Praat_BN_SMOTE0_IEMOCAP_ALL.model -T ".$pathsnapsounds."uploaded_audio_feat_class.arff -p 0 > ".$pathsnapsounds."results_uploaded_audio.res");
 
/* return result class */
$v = exec($get_result_class) - 2;

/* classify feature file against the arousal model */
  exec("java -cp ".$strWeka." weka.classifiers.bayes.BayesNet -l ".$strmodel."model_dominance_Praat_BN_SMOTE0_IEMOCAP_ALL.model -T ".$pathsnapsounds."uploaded_audio_feat_class.arff -p 0 > ".$pathsnapsounds."results_uploaded_audio.res");
 
/* return result class */
$d = exec($get_result_class) - 2;

echo json_encode( array ('arousal' => $a, 'pleasure' => $v, 'dominance' =>$d) );

?>
