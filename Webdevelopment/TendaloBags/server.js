import express from "express";
import axios from "axios";
const app = express();
const port = 3000;
app.use(express.static("public"));
app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(express.static('public'));
app.get("/",  (req, res) => {
    res.render("home")
});

app.get('/about', (req, res) => {
  res.render('about');
});
app.get('/login', (req, res) => {
  res.render('login');
});
app.get('/sign-up', (req, res) => {
  res.render('sign-up');
});
app.get('/cart', (req, res) => {
  res.render('cart');
});
app.get('/account', (req, res) => {
  res.render('sign-up');
});
app.post('/login', (req, res) => {
  res.render("account")
});
app.listen(port, () => {
  console.log(`Server running on port: ${port}`);
});