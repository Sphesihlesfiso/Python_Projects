import React from "react";
import SectionItem from "./Sections";
import {
  House,
  PersonWorkspace,
  Award,
  Wrench,
  EnvelopeFill,
  FilePerson
} from "react-bootstrap-icons";

function Header() {
  return (
    <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
      <SectionItem name="Home" svg={House} />
      <SectionItem name="Projects" svg={PersonWorkspace} />
      <SectionItem name="Skills" svg={Award} />
      <SectionItem name="Tools" svg={Wrench} />
      <SectionItem name="Contact" svg={EnvelopeFill} />
      <SectionItem name="Resume" svg={FilePerson} />
    </div>
  );
}

export default Header;
