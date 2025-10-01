import React from "react";
import SectionItem from "./Sections";

function Header() {
  return (
    <header>
    <div style={{ display: "flex", alignItems: "center",justifyItems:"center",justifyContent:"space-around",borderRadius:"10px"}}>
      <SectionItem name="Home" />
      <SectionItem name="Projects" />
      <SectionItem name="Skills" />
      <SectionItem name="Contact" />
    </div>
    </header>
  );
}

export default Header;
