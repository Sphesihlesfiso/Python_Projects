import React from "react-dom"

function SectionItem(props){
    const Icon = props.svg;
    return(
        <div style={{ display: 'block', alignItems: 'center', textAlign:'center', padding:"2px"}}>
            <Icon size={24} />
            <p style={{ margin: 0 }}>{props.name}</p>
        </div>

    )
}
export default SectionItem;