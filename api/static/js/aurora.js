class FlowField {
    settings = {
        // Defaults:
        frequency: 0.2,
    }

    constructor(w, h, settings = {}) {
        this.settings = { ...this.settings, ...settings };
        this.w = w || 10;
        this.h = h || 10;
        this.time = 0;

        this.build();
    }

    build() {
        this.cols = Math.ceil(this.w);
        this.rows = Math.ceil(this.h);

        // Prepare columns
        this.field = new Array(this.cols);
        for (let x = 0; x < this.cols; x++) {
            // Prepare rows
            this.field[x] = new Array(this.rows);
            for (let y = 0; y < this.rows; y++) {
                // Prepare data
                this.field[x][y] = new Vector(0, 0);
            }
        }
    }

    update(delta) {
        this.time += delta;

        const updateTime = this.time * this.settings.frequency / 1000;
        for (let x = 0; x < this.field.length; x++) {
            for (let y = 0; y < this.field[x].length; y++) {
                // Update field
                const angle = noise.simplex3(x / 20, y / 20, updateTime) * Math.PI * 2;
                const length = noise.simplex3(x / 10 + 40000, y / 10 + 40000, updateTime);
                this.field[x][y].setAngle(angle);
                this.field[x][y].setLength(length);

                // Manipulate vector
                if (typeof this.manipulateVector === 'function') {
                    this.manipulateVector(this.field[x][y], x, y);
                }

                // Render field
                if (typeof this.onDraw === 'function') {
                    this.onDraw(this.field[x][y], x, y);
                }
            }
        }
    }
}

/******************
 ** Example code **
 ******************/
// Note, this is not built dynamically. For production I'd make it the instance code here much more dynamic and more developer-friendly

// Setting
const settings = {
    frequency: 0.1,
}
const tileSize = 40; // Pixel width of tiles
const tileRatio = 2; // y/x ratio

// Setup
const canvas = document.getElementById('flowfield');
const ctx = canvas.getContext('2d');
const box = canvas.getBoundingClientRect();
const container = canvas.parentElement;

// Set up height to match full container size
canvas.height = box.width * (container.clientHeight / container.clientWidth);
canvas.width = box.width;

// Flowfield setup
const cols = Math.ceil(container.clientWidth / tileSize);
const rows = Math.ceil(container.clientHeight / (tileSize * tileRatio));

const ctxScale = {
    x: canvas.width / cols,
    y: canvas.height / rows,
}
const widthColorScaling = 255 / cols;
const heightColorScaling = 255 / rows;

// Mouse manip setup
const mouse = new Vector(0, 0);

// Init flowfield
const ff = new FlowField(cols, rows, settings);

