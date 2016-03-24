
initialize = function(){
		var informationAgent = null;
		var connectionAgent = null; 
		
		//var canvas = document.getElementById(videocanvas);
	
	informationAgent = new InformationAgent();
	connectionAgent = new ConnectionAgent();
	informationAgent.setSnapshot(true);
	informationAgent.setSnapShotCanvas(canvas);
	connectionAgent.setVideoContainer(document.getElementById("videoContainer"));
	connectionAgent.start();
	informationAgent.start();
};

	
	


