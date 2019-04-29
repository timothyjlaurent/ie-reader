import React from "react";
import Graph from "react-graph-vis";


const GraphRenderer = ({graph}) => {

  const options = {
    layout: {
      hierarchical: {
        enabled: true,
        direction: "LR",
        sortMethod: "directed",
        edgeMinimization: true,
        treeSpacing: 100,
        levelSeparation: 320,
        nodeSpacing: 20,
        blockShifting: true,
        parentCentralization: true,
        hubsize: "directed",
      },
      // hierarchical: false
    },
    edges: {
      color: "#000000",
      font:{
        vadjust:0,
        size: 16,
        bold: true,
        align: "top",
        multi: true
      },
      smooth: {
        type: "dynamic",
        roundness: 0.45
      },
      shadow: true,
      length: 30,
      scaling: {
        label: true
      }
    },
    nodes: {
      shape: "text",
      // fixed: false,
      widthConstraint: 90,
      font: {
          background: "transparent"

      }
    },
    height:1080,
    width: 1080,

  };

  const events = {
    //TODO connect graph events with application
    select: function(event) {
      const { nodes, edges } = event;
    }
  };
  return (
    <Graph
      graph={graph}
      options={options}
      events={events}
      getNetwork={network => {
        //  if you want access to vis.js network api you can set the state in a parent component using this property
      }}
    />
  );
}

export default GraphRenderer;
