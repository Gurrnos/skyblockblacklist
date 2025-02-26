const express = require('express');
const cors = require('cors');
const app = express();
const db = require("better-sqlite3")("skyblockshitters.db");

// Use cors
app.use(cors());
app.use(express.json());


// Database table creation
db.prepare(`
  CREATE TABLE IF NOT EXISTS Shitterlist(
  id INTEGER PRIMARY KEY, 
  username TEXT NOT NULL, 
  area TEXT NOT NULL, 
  reason TEXT NOT NULL,
  addedBy TEXT NOT NULL
  )
`).run();


// Add user to the blacklist, with field data from discord bot command
app.post("/addUser", function(req, res){
  const { username, area, reason, addedBy } = req.body;

  if (!username || !area || !reason || !addedBy) {
    return res.status(400).send("All fields are required")
  }

  if (username.length > 50 || area.length > 50 || reason.length > 150) {
    return res.status(410).send("Input exceeded character limit");
  }
  

  const existingUser = db.prepare("SELECT * FROM Shitterlist WHERE username = ?").get(username);

  if (existingUser) {
    return res.status(409).send("User already exists on the list");
  }

  const stmt = db.prepare("INSERT INTO Shitterlist(username, area, reason, addedBy) VALUES (?, ?, ?, ?)")
  stmt.run(username, area, reason, addedBy);

  res.status(200).send("User added");
})


// Check if a user is on the list, if it is, get all the data and send as a response
app.get("/checkUser", function(req, res) {
  const { username } = req.query;

  const findUser = db.prepare("SELECT * FROM Shitterlist WHERE username = ?").get(username);

  if (!findUser) {
    return res.status(404).send({ message: `${username} not found on the list` });
  }

  res.json(findUser);
})


// Find all users currently on the list
app.get("/findAll", function (req, res) {
  const findAll = db.prepare("SELECT * FROM Shitterlist").all()

  if(findAll.lenght === 0) {
    return res.status(404).send({ message: "The shitter list is empty" });
  }

  res.json(findAll)
})


// Delete user from the list
app.delete("/deleteUser", function (req, res) {
  const { username } = req.body;

  const existingUser = db.prepare("SELECT * FROM Shitterlist WHERE username = ?").get(username);

  if (!existingUser) {
    return res.status(404).send({ message: `${username} is not on the list.` });
  }
  
  const deleteUser = db.prepare("DELETE FROM Shitterlist WHERE username = ?").run(username);

  if (deleteUser.changes > 0) {
    res.status(200).send({ message: `${username} has been removed from the shitter list.` });
  } else {
    res.status(500).send({ message: `Failed to remove ${username} from the shitter list.` });
  }
});

// Run server
app.listen(3000, () =>
  console.log("Server is running on http://localhost:" + 3000)
);