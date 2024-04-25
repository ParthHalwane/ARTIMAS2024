const CANVAS = document.querySelector("canvas"),
    CTX = CANVAS.getContext("2d"),
    W = window.innerWidth,
    H = window.innerHeight,
    XO = W / 2,
    YO = H / 2,
    NUM_PARTICLES = 300, // Reduced number of particles
    MAX_Z = 4,
    MAX_R = 5, // Increased particle size
    Z_SPD = 2,
    PARTICLES = [];

class Particle {
    constructor(x, y, z) {
        this.pos = new Vector(x, y, z);
        const X_VEL = (Math.random() - 0.5) * 0.2,
            Y_VEL = (Math.random() - 0.5) * 0.2,
            Z_VEL = -Z_SPD;
        this.vel = new Vector(X_VEL, Y_VEL, Z_VEL);
        this.vel.scale(0.01);

        // Generate brighter variations of orange and blue colors
        const red = Math.floor(Math.random() * 100) + 155; // Adjust the range for different shades
        const green = Math.floor(Math.random() * 100) + 155; // Adjust the range for different shades
        const blue = Math.floor(Math.random() * 100) + 155; // Adjust the range for different shades

        // Ensure that the colors are close to white by combining them
        this.stroke = `rgb(${red}, ${green}, ${blue})`;
    }

    update() {
        this.pos.add(this.vel);
    }

    render() {
        const PIXEL = to2d(this.pos),
            X = PIXEL[0],
            Y = PIXEL[1],
            R = (MAX_Z - this.pos.z) / MAX_Z * MAX_R;

        if (X < 0 || X > W || Y < 0 || Y > H) this.pos.z = MAX_Z;

        this.update();

        // Add a shining effect with shadowBlur
        CTX.beginPath();
        CTX.fillStyle = this.stroke;
        CTX.arc(X, PIXEL[1], R, 0, Math.PI * 2);

        // Customize the shadowBlur properties for the shining effect
        CTX.shadowColor = this.stroke;
        CTX.shadowBlur = 10; // Adjust this value to control the intensity of the shining effect

        CTX.fill();
        CTX.closePath();

        // Reset shadowBlur after drawing each particle
        CTX.shadowBlur = 0;
    }

}

class Vector {
    constructor(x, y, z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    add(v) {
        this.x += v.x;
        this.y += v.y;
        this.z += v.z;
    }

    scale(n) {
        this.x *= n;
        this.y *= n;
        this.z *= n;
    }
}

function to2d(v) {
    const X_COORD = v.x - XO,
        Y_COORD = v.y - YO,
        PX = X_COORD / v.z,
        PY = Y_COORD / v.z;
    return [PX + XO, PY + YO];
}

function render() {
    for (let i = 0; i < PARTICLES.length; i++) {
        PARTICLES[i].render();
    }
}

function loop() {
    requestAnimationFrame(loop);
    CTX.fillStyle = "rgba(0,0,0,0.1)";
    CTX.fillRect(0, 0, W, H);
    render();
}

function createParticles() {
    for (let i = 0; i < NUM_PARTICLES; i++) {
        const X = Math.random() * W, Y = Math.random() * H, Z = Math.random() * MAX_Z;
        PARTICLES.push(new Particle(X, Y, Z));
    }
}

function init() {
    CANVAS.width = W;
    CANVAS.height = H;
    createParticles();
    // increaseSpeed();
    loop();
}

function increaseSpeed() {
    PARTICLES.forEach(particle => {
        particle.vel.z -= 3; // Increase the speed by adjusting Z velocity
    });
}




init();
