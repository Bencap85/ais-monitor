const { io } = require("socket.io-client");

const socket = io("http://localhost:5000");

socket.on("connect", () => {
  console.log("Connected");
  socket.emit("subscribe_tiles", {
    tiles: ["6_18_24", "6_18_25"]
  });

  
});

socket.on("ais_update", (data) => {
  console.log("Received update:", data);
});