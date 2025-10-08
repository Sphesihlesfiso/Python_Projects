import express from "express";
import pg from "pg";
import https from 'https';
import fs from 'fs';
import multer from "multer"
import passport from "passport";
import { Strategy } from "passport-local";
import session from "express-session";
import env from "dotenv";
import bcrypt  from "bcrypt"
import crypto from "crypto";
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
env.config();
const options = {
  key: fs.readFileSync('./ssl/private.key'),
  cert: fs.readFileSync('./ssl/certificate.crt')
};
const app = express();
const port = process.env.port;
app.use(express.static("public"));
app.use('/uploads', express.static('public/uploads'));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.set('view engine', 'ejs');

const saltRounds = 10;


app.use(
  session({
    secret: process.env.key,
    resave: false,
    saveUninitialized: false,
    cookie:{ secure:false,
      maxAge:1000*60*60*24*5
    }
  })
);


app.use(passport.initialize());
app.use(passport.session());
const dataBase=new pg.Client({
    user:process.env.user,
    host:process.env.host,
    database:process.env.database,
    password:process.env.password,
    port:process.env.db_p,
});

dataBase.connect();


function fetchBagsFromdataBase() {

  return new Promise((resolve, reject) => {
    dataBase.query("SELECT * FROM pictures", (err, res) => {
      if (err) {
        console.error("Error executing query", err.stack);
        reject(err);
      } else {
        resolve(res.rows);
      }
    });
  });
}

app.get("/", async (req, res) => {
  try {
    console.log("INNNNNNNNNNNNNNNNNNNN");

    // Fetch all bags (available products)
    const cars = await fetchBagsFromdataBase();

    let bagsIncart = [];

    if (req.user) {
      
      console.log(`user id: ${req.user.id}`);

      const orders_result = await dataBase.query(
        "SELECT * FROM orders WHERE orders.user_id=$1",
        [req.user.id]
      );

      bagsIncart = orders_result.rows.map(row => row.bag_id);
    } else {
      
      console.log("User not logged in, showing empty cart.");
    }

    // Render page with either cart items or empty cart
    res.render("home", { cars, bagsIncart });
  } catch (err) {
    console.error(err);
    res.status(500).send("Error loading products");
  }
});


const storage = multer.diskStorage({
  destination: "./public/uploads/",
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  },
});
const upload = multer({ storage });

app.post("/upload", upload.single("image"), (req, res) => {
  const { name, price, available_bags } = req.body;
  const image = req.file.filename;

 
  const query = `
    INSERT INTO pictures (name,price,image,available_bags)
    VALUES ($1, $2, $3, $4)
  `;
  const values = [name, price,image,available_bags];

  dataBase.query(query, values, (err) => {
    if (err) {
      console.error("Upload error:", err.stack);
      res.status(500).send("Upload failed");
    } else {
      res.redirect("/");
    }
  });
});

app.get("/logout", (req, res) => {
  req.logout(function (err) {
    if (err) {
      return next(err);
    }
    res.redirect("/");
  });
});

app.get("/account", (req, res) => {
  if (req.isAuthenticated() && req.user) {
    console.log(`User inside: ${req.user.id}`);

    if (req.user.id === 7) {
      console.log("admin");
      return res.render("upload");
    } else {
      console.log("non admin");
      return res.render("account");
    }
  } else {
    console.log("not authenticated");
    return res.redirect("/login");
  }
});


app.post("/login",
  passport.authenticate("local", {
    
    successRedirect: "/account" ,
    failureRedirect: "/login",
  })
);

app.post("/register", async (req, res) => {
  const email = req.body.username;
  const password = req.body.password;
  console.log(email,password)

  try {
    const checkResult = await dataBase.query("SELECT * FROM users WHERE email = $1", [
      email,
    ]);

    if (checkResult.rows.length > 0) {
      res.redirect("/login");
    } else {
      bcrypt.hash(password, saltRounds, async (err, hash) => {
        if (err) {
          console.error("Error hashing password:", err);
        } else {
          const result = await dataBase.query(
            "INSERT INTO users (email, password) VALUES ($1, $2) RETURNING *",
            [email, hash]
          );
          const user = result.rows[0];
          req.login(user, (err) => {

            console.log(email);
            res.redirect("/account");
          });
        }
      });
    }
  } catch (err) {
    console.log(err);
  }
});

passport.use(
  new Strategy(async function verify(username, password, cb) {
    try {
      const result = await dataBase.query("SELECT * FROM users WHERE email = $1 ", [
        username,
      ]);
      if (result.rows.length > 0) {
        const user = result.rows[0];
        const storedHashedPassword = user.password;
        bcrypt.compare(password, storedHashedPassword, (err, valid) => {
          if (err) {
            //Error with password check
            console.error("Error comparing passwords:", err);
            return cb(err);
          } else {
            if (valid) {
              //Passed password check
              return cb(null, user);
            } else {
              //Did not pass password check
              return cb(null, false);
            }
          }
        });
      } else {
        return cb("User not found");
      }
    } catch (err) {
      console.log(err);
    }
  })
);

passport.serializeUser((user, cb) => {
  cb(null, user);
});
passport.deserializeUser((user, cb) => {
  cb(null, user);
});
console.log("outside")






app.get("/checkout", (req, res) => {
  const paymentData = {
  merchant_id: "10000100",
  merchant_key: "46f0cd694581a",
  return_url: "https://d0df5321a769.ngrok-free.app",
  cancel_url: "https://547cfb2939e8.ngrok-free.app/cart",
  notify_url: "https://547cfb2939e8.ngrok-free.app/about",
  name_first: "John",
  name_last: "Doe",
  email_address: "mabasosphesihle25@gmail.com",
  amount: "20500", // R50
  item_name: "Test Product",
};

  // Create the query string
  const queryString = Object.keys(paymentData)
    .map(key => `${key}=${encodeURIComponent(paymentData[key])}`)
    .join("&");

  // Redirect user to PayFast sandbox
  
  const PAYFAST_URL="https://sandbox.payfast.co.za/eng/process"

  res.redirect(`${PAYFAST_URL}?${queryString}`);
});

console.log("OUTSIDE")
app.delete("/removeFromCart",async (req,res)=>{
  console.log("INSIDE")
  const {bag_id}=req.body;
  console.log(bag_id);
  await dataBase.query(`DELETE FROM orders WHERE bag_id=$1`,[bag_id]);
   res.status(200).json({ message: "Item removed" });
})
app.post("/addBag", async (req, res) => {
  console.log("inside")
  
  try {
    const { bag_id } = req.body;
    const user = req.user;
    console.log(`User put or not ${req.user}`)
    const result = await dataBase.query(
      "INSERT INTO orders (bag_id,user_id) VALUES ($1,$2)  RETURNING *",
      [bag_id,user.id]
    );

    console.log("Inserted order:", result.rows[0]);

    res.status(201).json({ order: result.rows[0] });
  } catch (err) {
    console.error("Insert failed:", err);
    res.status(500).json({ error: "Query failed" });
  }
});

app.get('/upload',async (req, res) => {
    res.render('upload');

  

});
app.get('/about',async (req, res) => {
  res.render('about');
});
app.get('/login', (req, res) => {
  
    res.render("login")
});


app.get('/register', (req, res) => {
  res.render('register');
});

app.get('/cart',async (req, res) => {
  if (req.isAuthenticated()){ 
    try {
      const user = req.user;
      console.log("User in:", user.id);

      
      const result = await dataBase.query(`
      SELECT pictures.*
      FROM pictures
      JOIN orders ON pictures.bag_id = orders.bag_id  AND orders.user_id =$1
    `,[user.id]);
      
       res.render("cart",{bagsIncart:result.rows});
    } catch (error) {
      console.error("Error",error)
    }
   
  } else {
    res.redirect("/login");}
});
app.post('/register', (req, res) => {
  res.render('register');
});

https.createServer(options, app).listen(port, () => {
  console.log(`Secure server running on https://localhost ${port}`);
});