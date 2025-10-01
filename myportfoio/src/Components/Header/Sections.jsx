import React from "react-dom"

function SectionItem(props){
    return(
        <div className="HeaderItems" >
            <p style={{padding:"10px"}}>{props.name}</p>
        </div>

    )
}
export default SectionItem;