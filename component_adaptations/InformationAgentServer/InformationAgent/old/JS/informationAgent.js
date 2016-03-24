// Information Agent v0.01


function InformationAgent(){
		var canvasID				= null;
		var clientIP 				= null;
		var snapShot				= false;
		var snapshotStorageLocation = "";
	
	
	//PUBLIC methods
	
	this.getClientIP 	= function(){return clientIP;};
	
	this.setSnapshot	= function(boolValue){
		snapShot = boolValue;
		setInterval(saveFile, 60000);
		};
		
	this.setSnapShotCanvas = function(canvas){ canvasID = canvas;};
	
	this.setSnapshotStorageLocation = function(strValue){snapshotStorageLocation  = strValue;};
	
	
	//PRIVATE methods
	saveFile = function(){
			var dataURL = canvasID.toDataURL('image/png');
		$.ajax({
  			type: "POST",
  			url: "../PHP/saveSnapShot.php",
  			img: { 
				data:{
     				imgBase64: dataURL}
  					}
				});
	};
	
	// populate the object
	
	$.get("../PHP/getIP.php", function(ip){
		clientIP = ip;
		console.log(clientIP);}
		);


	 }; //end of InformationAgent
	 
 //end of file


	
	


