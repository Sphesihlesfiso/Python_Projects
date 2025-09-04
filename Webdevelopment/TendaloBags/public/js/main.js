document.querySelectorAll(".btn.btn-outline-dark.mt-auto").forEach(button => {
  button.addEventListener("click", e => {
    e.preventDefault();

    const bagid = button.id; // unique per button
    console.log(button.id)
    fetch("/addBag", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bag_id: bagid })
    })
    .then(res => res.json())
    .then(data => {
      console.log("Bag added:", data);
      window.location.reload();

    })
    .catch(err => console.error("Error:", err));
  });
});
const trashBtns=document.querySelectorAll(".bi.bi-trash.remove-btn");
trashBtns.forEach(trashBtn => {
  trashBtn.addEventListener("click",()=>{
    const trashId=trashBtn.id;
    fetch("/removeFromCart", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bag_id: trashId })
    })
    .then(res => res.json())
    .then(data=>{
      console.log("Reloading now...")
      window.location.reload();
    })
    .catch(err => console.error("Error:", err));
  });
});
// fetch("/checkout",{
//   method:'POST',
//   headers: {
//     'Content-Type': 'application/json'
//   },
//   body:JSON.stringify({
//   })

// }).then(res=>{
//     if (res.ok) return res.json()
//       return res.json.then(json=>Promise.reject(json))
//   }).then(({url}) =>{
//     window.location=url
//   }).catch(e=>{
//     console.error(e.error)
//   })

