module.exports = {
  apps : [{
    name: "dr-owl-ui",
    script: "npx",
    args: "serve -s build -l 3000",
    interpreter: "none",
    env: {
      NODE_ENV: "production",
    }
  }]
}