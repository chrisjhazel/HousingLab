function init() {
    var scene = new THREE.Scene();
    var gui = new dat.GUI();

    var enableFog = false;

    if (enableFog) {
        scene.fog = new THREE.FogExp2(0xffffff, 0.2);
    }

    // set some global values
    //May need to relocate these down the road
    const tradColor = 'rgb(87, 150, 217)';
    const semiColor = 'rgb(137, 217, 87)';
    const fullColor = 'rgb(206, 219, 83)';
    const aprtColor = 'rgb(224, 105, 105)';

    var 



    var camera = new THREE.PerspectiveCamera(
		45,
		window.innerWidth/window.innerHeight,
		1,
		1000
    );
    camera.position.z = 5;
    camera.position.x = 1;
    camera.position.y = 2;

    camera.lookAt(new THREE.Vector3(0,0,0));

	var renderer = new THREE.WebGLRenderer();
    renderer.shadowMap.enabled = true;
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor('rgb(120, 120, 120)');
	document.getElementById('webgl').appendChild(renderer.domElement);
	
    var controls = new THREE.OrbitControls(camera, renderer.domElement);

    update(renderer, scene, camera, controls);
    
    return scene;
}

function getPlane(size) {
    var geometry = new THREE.PlaneGeomtry(size, size);
    var material = new THREE.MeshPhongMaterial({
        color: 'rgb(120, 120, 120)',
        side: THREE.DoubleSide
    });

    var mesh = new THREE.Mesh(
        geometry,
        material
    );

    mesh.receiveShadown = true;

    return mesh;
}

function getBox(w, h, d, col, x_pl, y_pl, z_pl) {
    //input width, height, depth, color, and placement
    var geometry = new THREE.BoxGeometry(w,h,d);
    var material = new THREE.MeshPhongMaterial({
        color: col
    });
    
    geometry.placement.x = x_pl;
    geometry.placement.y = y_pl;
    geometry.placement.z = z_pl;

    var mesh = new THREE.Mesh(
        geometry, 
        material
    );
    mesh.castShadow = true;

    return mesh;
}

function update(renderer, scene, camera, controls) {
    renderer.render(
        scene, 
        camera
    );

    controls.update();

    requestAnimationFrame(function(){
        update(renderer, scene, camera, controls);
    })
}

function layoutBar(unitMix) {
    //Setup array to capture all of the blocks
    var geoBlox = [];

    //Set up position variables
    var x_pl = 0;
    var y_pl = 0;
    var z_pl = 0;



}


var scene = init();