import MakeResume from "../buttons/MakeResume";
import Header from "../HeadFoot/Header.tsx";
import Chatbox from "../chatbox/chatbox.tsx";
import Footer from "../HeadFoot/Footer.tsx";
export default function Landing(){
    return(
        <>
        <Header></Header>
        <MakeResume></MakeResume>
        <Chatbox></Chatbox>
        <Footer></Footer>
        </>
    )
}