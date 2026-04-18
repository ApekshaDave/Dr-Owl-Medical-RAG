const { exec } = require('child_process');
console.log("Starting Dr. Owl UI server...");
const serve = exec('npx serve -s build -l 3000');
serve.stdout.on('data', console.log);
serve.stderr.on('data', console.error);