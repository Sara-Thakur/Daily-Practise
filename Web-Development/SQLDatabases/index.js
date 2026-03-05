const { faker } = require("@faker-js/faker");
const mysql = require("mysql2");
const express = require("express");
const app = express();
const path = require("path");
const methodOverride = require("method-override");
// const {v4:uuidv4}=require("uuid");

app.use(methodOverride("_method"));
app.use(express.urlencoded({ extended: true }));
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "/views"));

let connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  database: "delta",
  password: "sara",
});

// try{
// connection.query("show tables",(err,result)=>{
//     if(err) throw err;
//     console.log(result);

// });
// }catch(err){
//     console.log(err);
// }
// let  getRandomUser=()=> {
//     return {
//       id: faker.string.uuid(),
//       username: faker.internet.username(),
//       email: faker.internet.email(),
//     //   avatar: faker.image.avatar(),
//       password: faker.internet.password(),
//     //   birthdate: faker.date.birthdate(),
//     //   registeredAt: faker.date.past(),
//     };
//   }
// console.log(getRandomUser());

// let q="INSERT INTO user(id,username,email,password) VALUES (?,?,?,?)";
// let user=["123","abcs","abc@gmailcom","adds"];

let getRandomUser = () => {
  return [
    faker.string.uuid(),
    faker.internet.username(),
    faker.internet.email(),

    faker.internet.password(),
  ];
};
// let q="INSERT INTO user(id,username,email,password) VALUES ?";
// let data=[];
// for(let i=1;i<=100;i++){
//   data.push(getRandomUser());
// }

// try{
//   connection.query(q,[data],(err,result)=>{
//     if(err) {
//       console.log(err);
//       return;
//     }
//     console.log(result);

//   });
//   }catch(err){
//       console.log(err);
//   }

//connection.end();//close connection with sql
app.get("/", (req, res) => {
  // 1. Use an alias 'count' for easier access
  let q = "SELECT COUNT(*) AS count FROM user";

  connection.query(q, (err, result) => {
    if (err) {
      console.error("Database Error:", err);
      return res.status(500).send("Error fetching data");
    }

    // 2. Access the alias 'count' defined in the query
    let count = result[0].count;

    console.log("User count from database:", count);

    // 3. Render the page
    res.render("home.ejs", { count });
  });
});

// show
app.get("/users", (req, res) => {
  // 1. Use an alias 'count' for easier access
  let q = "SELECT * FROM user";
  try {
    connection.query(q, (err, users) => {
      if (err) throw err;
      res.render("showuser.ejs", { users });
    });
  } catch (err) {
    console.log(err);
    res.send("some error in db");
  }
});

// edit
app.get("/user/:id/edit", (req, res) => {
  let { id } = req.params;
  let q = `select * from user where id=?`;
  // console.log(id);
  try {
    connection.query(q, [id], (err, result) => {
      if (err) throw err;
      if (result.length === 0) {
        console.log("No user found for ID:", id);
        return res.status(404).send("User not found in database.");
      }
      console.log(result);
      //why this consolelog not working
      let user = result[0];
      res.render("edit.ejs", { user });
    });
  } catch (err) {
    console.log(err);
    res.send("some error in db");
  }
});

// update route
app.patch("/user/:id", (req, res) => {
  // res.send("updated");
  let { id } = req.params;
  let { password: formPass, username: newUsername } = req.body;
  let q = `select * from user where id=?`;
  try {
    connection.query(q, [id], (err, result) => {
      if (err) throw err;
      if (result.length === 0) {
        console.log("No user found for ID:", id);
        return res.status(404).send("User not found in database.");
      }
      console.log(result);
      //why this consolelog not working
      let user = result[0];
      if (formPass != user.password) {
        res.send("WRONG password");
      }
      // res.render("edit.ejs",{user});
      else {
        let q2 = `UPDATE user SET  username='${newUsername}' WHERE id='${id}'`;
        connection.query(q2, (err, result) => {
          if (err) throw err;
          res.redirect("/users");
          // res.send(result);
        });
      }
    });
  } catch (err) {
    console.log(err);
    res.send("some error in db");
  }
});

//delete
app.delete("/user/:id",(req,res)=>{
  let { id } = req.params;
  let q = `DELETE FROM user WHERE id=?`;
  // console.log(id);
  try {
    connection.query(q, [id], (err, result) => {
      if (err) throw err;
      

          res.redirect("/users");
          // res.send(result);
       
      // res.render("edit.ejs", { user });
    });
  } catch (err) {
    console.log(err);
    res.send("some error in db");
  }
});
//add
app.get("/user/add", (req, res) => {
  
      res.render("add.ejs");
   
});
app.post("/users",(req,res)=>{
  let {username,password,email,id}=req.body;
  // res.send("new user added");
  // // let id=uuidv4();
  let q=`insert into user (username,password,email,id) values (?,?,?,?) ;`;
  connection.query(q,[username,password,email,id] ,(err, result) => {
    if (err) throw err;
    res.redirect("/users");
    // res.send(result);
  });
  
});
app.listen("8080", () => {
  console.log("server is listening at port 8080");
});
