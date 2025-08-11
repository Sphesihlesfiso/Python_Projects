import express from "express";
import axios from "axios";
import pg from "pg";

const app = express();
const port = 3000;
app.use(express.static("public"));
app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(express.static('public'));
const dataBase=new pg.Client({
    user:"postgres",
    host:"localhost",
    database:"Bags",
    password:"1910",
    port:5432,
});

dataBase.connect();
const bags =[];

function fetchBagsFromDB() {
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
    const bags = await fetchBagsFromDB();
    res.render("home", { bags }); // Pass bags to your EJS or template engine
    console.log(bags)
  } catch (err) {
    res.status(500).send("Error loading products");
  } finally {
    // Close connection after query
  }
});


app.get('/about',async (req, res) => {
  res.render('about');
});
app.get('/login', (req, res) => {
  res.render('login');
});
app.get('/register', (req, res) => {
  res.render('register');
});
app.get('/cart', (req, res) => {
  res.render('cart');
});
app.post('/register', (req, res) => {
  res.render('register');
});
app.post('/login', (req, res) => {
  res.render("account")
});
app.get('/admin', (req, res) => {
  res.render("admindashboard")
});
app.get('/login/register', (req, res) => {
  res.render("joter")
});
app.post('/admin', (req, res) => {
  const nameofBag=req.body["Nameofbag"]
  console.log(nameofBag)
  res.render("admindashboard")
});
app.listen(port, () => {
  console.log(`Server running on port: ${port}`);
});