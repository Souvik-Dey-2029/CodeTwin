"use client";

import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

interface TreemapData {
  name: string;
  value?: number;
  children?: TreemapData[];
}

export default function RiskHeatmap({ data }: { data: TreemapData }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const width = 800;
    const height = 400;

    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height] as any)
      .attr("width", "100%")
      .attr("height", height);

    svg.selectAll("*").remove();

    const root = d3.hierarchy(data)
      .sum((d: any) => d.value || 0)
      .sort((a: any, b: any) => (b.value || 0) - (a.value || 0));

    d3.treemap<any>()
      .size([width, height])
      .padding(1)
      (root);

    const leaf = svg.selectAll("g")
      .data(root.leaves())
      .join("g")
      .attr("transform", (d: any) => `translate(${d.x0},${d.y0})`);

    leaf.append("rect")
      .attr("width", (d: any) => d.x1 - d.x0)
      .attr("height", (d: any) => d.y1 - d.y0)
      .attr("fill", (d: any) => {
          const val = d.data.value || 0;
          if (val > 40) return "#ef4444"; // Red
          if (val > 20) return "#f59e0b"; // Amber
          return "#10b981"; // Green
      })
      .attr("fill-opacity", 0.6)
      .attr("stroke", "#020617")
      .attr("stroke-width", 0.5);

    leaf.append("text")
      .attr("x", 5)
      .attr("y", 15)
      .attr("fill", "white")
      .attr("font-size", "10px")
      .attr("font-weight", "bold")
      .text((d: any) => d.data.name);

    leaf.append("title")
      .text((d: any) => `${d.data.name}\nRisk Score: ${d.data.value}`);

  }, [data]);

  return (
    <div className="bg-slate-900/50 rounded-2xl border border-slate-800 overflow-hidden">
      <svg ref={svgRef}></svg>
    </div>
  );
}
