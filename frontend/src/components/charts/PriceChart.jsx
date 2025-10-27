import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function PriceChart({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.actual || data.actual.length === 0) return;

    const svg = d3.select(svgRef.current)
      .attr('width', 800)
      .attr('height', 400);

    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 30, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime()
      .domain(d3.extent(data.actual, d => new Date(d.date)))
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data.actual, d => d.price)])
      .range([height, 0]);

    const line = d3.line()
      .x(d => x(new Date(d.date)))
      .y(d => y(d.price));

    g.append('path')
      .datum(data.actual)
      .attr('fill', 'none')
      .attr('stroke', '#3B82F6')
      .attr('stroke-width', 2)
      .attr('d', line);

    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    g.append('g')
      .call(d3.axisLeft(y));
  }, [data]);

  return (
    <div className="relative">
      <svg ref={svgRef}></svg>
    </div>
  );
}

export default PriceChart;