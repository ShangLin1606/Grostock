import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function HeatmapChart({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    const width = 800;
    const height = 400;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    svg.selectAll('*').remove();

    const xScale = d3.scaleBand()
      .domain(data.map(d => d.stock_id))
      .range([margin.left, width - margin.right])
      .padding(0.05);

    const yScale = d3.scaleBand()
      .domain(['漲跌幅'])
      .range([margin.top, height - margin.bottom])
      .padding(0.05);

    const colorScale = d3.scaleSequential(d3.interpolateRdYlGn)
      .domain([-0.1, 0.1]);

    svg.selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => xScale(d.stock_id))
      .attr('y', yScale('漲跌幅'))
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', d => colorScale(d.change));

    svg.append('g')
      .attr('transform', `translate(0, ${height - margin.bottom})`)
      .call(d3.axisBottom(xScale));

    svg.append('g')
      .attr('transform', `translate(${margin.left}, 0)`)
      .call(d3.axisLeft(yScale));
  }, [data]);

  return <svg ref={svgRef}></svg>;
}

export default HeatmapChart;