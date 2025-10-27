import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Link } from 'react-router-dom';

function HeatmapChart({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    console.log('開始渲染熱力圖', data);

    const width = 1000;
    const height = 600;
    const margin = { top: 50, right: 20, bottom: 50, left: 100 };

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    svg.selectAll('*').remove();

    if (!data || data.length === 0) {
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('fill', '#F3F4F6')
        .text('無熱力圖數據可用');
      return;
    }

    // 按關注度排序，取前10名
    const topStocks = data
      .sort((a, b) => (b.popularity_score || 0) - (a.popularity_score || 0))
      .slice(0, 10);

    if (topStocks.length === 0) {
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('fill', '#F3F4F6')
        .text('無關注度數據可用');
      return;
    }

    const groupedData = d3.group(topStocks, d => d.industry || '其他');
    const industries = Array.from(groupedData.keys());

    const blocksPerRow = Math.ceil(Math.sqrt(topStocks.length));
    const blockWidth = (width - margin.left - margin.right) / blocksPerRow;
    const blockHeight = (height - margin.top - margin.bottom) / blocksPerRow;

    const colorScale = d3.scaleLinear()
      .domain([-0.1, 0, 0.1])
      .range(['#10B981', '#9CA3AF', '#F43F5E']); // 綠色、中性、紅色

    const sizeScale = d3.scaleSqrt()
      .domain([0, d3.max(topStocks, d => d.popularity_score || 1)])
      .range([20, blockWidth * 0.8]);

    let xOffset = margin.left;
    let yOffset = margin.top;

    industries.forEach(industry => {
      const stocks = groupedData.get(industry);
      const group = svg.append('g')
        .attr('transform', `translate(${xOffset}, ${yOffset})`);

      group.append('text')
        .attr('x', 0)
        .attr('y', -10)
        .attr('fill', '#F3F4F6')
        .text(industry);

      group.selectAll('rect')
        .data(stocks)
        .enter()
        .append('rect')
        .attr('x', (d, i) => (i % blocksPerRow) * blockWidth)
        .attr('y', (d, i) => Math.floor(i / blocksPerRow) * blockHeight)
        .attr('width', d => sizeScale(d.popularity_score || 1))
        .attr('height', d => sizeScale(d.popularity_score || 1))
        .attr('fill', d => {
          const change = d.change || 0;
          return colorScale(change);
        })
        .attr('stroke', '#9CA3AF')
        .attr('stroke-width', 1)
        .on('mouseover', function(event, d) {
          d3.select(this).attr('opacity', 0.7);
          const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('background', '#2D3748')
            .style('color', '#F3F4F6')
            .style('padding', '8px')
            .style('border-radius', '4px')
            .html(`股票: ${d.stock_id}<br>名稱: ${d.stock_name || '未知'}<br>漲跌幅: ${(d.change * 100).toFixed(2)}%<br>關注度: ${d.popularity_score?.toFixed(2) || 'N/A'}`);
          tooltip.style('left', `${event.pageX + 10}px`)
            .style('top', `${event.pageY - 10}px`);
        })
        .on('mouseout', function() {
          d3.select(this).attr('opacity', 1);
          d3.select('.tooltip').remove();
        });

      group.selectAll('text.stock-label')
        .data(stocks)
        .enter()
        .append('text')
        .attr('class', 'stock-label')
        .attr('x', (d, i) => (i % blocksPerRow) * blockWidth + blockWidth / 2)
        .attr('y', (d, i) => Math.floor(i / blocksPerRow) * blockHeight + blockHeight / 2)
        .attr('text-anchor', 'middle')
        .attr('fill', '#F3F4F6')
        .attr('font-size', '12px')
        .text(d => d.stock_id);

      yOffset += Math.ceil(stocks.length / blocksPerRow) * blockHeight + 50;
      if (yOffset > height - margin.bottom) {
        yOffset = margin.top;
        xOffset += (width - margin.left - margin.right) / 2;
      }
    });

    console.log('熱力圖渲染完成');
  }, [data]);

  return (
    <div className="relative">
      <svg ref={svgRef}></svg>
      <style>{`
        .tooltip {
          z-index: 10;
        }
      `}</style>
    </div>
  );
}

export default HeatmapChart;