import React, { useEffect, useState, useReducer } from "react";
import "./App.css";

import { Input, Layout, Divider, Row, Col } from "antd";

import { Formik, Form } from "formik";

import Select from "react-select";
import Button from "antd/es/button";

import GraphRenderer from "./GraphRenderer"
import InputForm from "./InputForm";

const { Header, Content, Footer } = Layout;

function Title() {
  return (
    <div className={"App-header"}>
      <header className={"App-header"}>IE-Reader</header>
    </div>
  );
}

const emptyGraph = {
  nodes: [],
  edges: []
}


const AppLayout = () => {
  const [ graph, setGraph ] = useState(emptyGraph)

  return (
  <div>
    <Row>
      <Col span={8} offset={1}>
        <InputForm updateGraph={setGraph} />
      </Col>
      <Col span={15}>
        <GraphRenderer graph={graph} />
      </Col>
    </Row>
  </div>
 );
};


function App() {
  return (
    <div className="App">
      <Layout style={{ height: "100vh" }}>
        <Header className={"header"}>
          <Title />
        </Header>
        <Content>
          <AppLayout/>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          IE-Reader
        </Footer>
      </Layout>
    </div>
  );
}

export default App;
