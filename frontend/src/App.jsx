import { useState, useEffect } from 'react' 
import axios from 'axios'
import Plot from 'react-plotly.js'
import './App.css'

function App() {
  const [sectorId, setSectorId] = useState(151)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showGroundTruth, setShowGroundTruth] = useState(false) // TOGGLE STATE
  const [activeTab, setActiveTab] = useState('flight')
  const [frames, setFrames] = useState([])
  const [roverTrace, setRoverTrace] = useState({})
  const [pathTrace, setPathTrace] = useState({})

  useEffect(() => { handleScan() }, [])

  useEffect(() => {
    if (data && data.path_coords && data.terrain_z) {
      prepare3DVisuals()
    }
  }, [data])

  const handleScan = () => {
    setLoading(true)
    setShowGroundTruth(false) 
    axios.get(`${import.meta.env.VITE_API_URL}/api/analyze/${sectorId}`)
      .then(res => { setData(res.data); setLoading(false); })
      .catch(err => { console.error(err); setLoading(false); })
  }

  const prepare3DVisuals = () => {
    const terrain = data.terrain_z.map(row => row.map(val => val * 0.05));
    
    const pathX = data.path_coords.map(p => p[1])
    const pathY = data.path_coords.map(p => p[0])
    const pathZ = data.path_coords.map(p => (data.terrain_z[p[0]][p[1]] * 0.05) + 1)

    setPathTrace({
      type: 'scatter3d', mode: 'lines', x: pathX, y: pathY, z: pathZ,
      line: { color: '#00FF00', width: 6 }
    })

    setRoverTrace({
      type: 'scatter3d', mode: 'markers', x: [pathX[0]], y: [pathY[0]], z: [pathZ[0]],
      marker: { color: '#FF4500', size: 5, symbol: 'diamond' }
    })

    const newFrames = []
    const step = Math.max(1, Math.floor(pathX.length / 50)) 
    
    for (let i = 0; i < pathX.length; i += step) {
      newFrames.push({
        name: `frame_${i}`,
        data: [
          { z: terrain }, 
          { x: pathX, y: pathY, z: pathZ }, 
          { x: [pathX[i]], y: [pathY[i]], z: [pathZ[i]] }
        ]
      })
    }
    setFrames(newFrames)
  }

  const getTerrainData = () => {
    if (data && data.terrain_z) {
        return data.terrain_z.map(row => row.map(val => val * 0.05));
    }
    return Array(20).fill(Array(20).fill(1));
  }

  const getGraphData = () => {
    if (!data || !data.path_coords || !data.terrain_z) return { x: [], y: [] };

    const coords = data.path_coords;
    const y = coords.map(p => (data.terrain_z[p[0]][p[1]] * 0.05) + 1);

    const x = [];
    let cum = 0;
    x.push(0);
    for (let i = 1; i < coords.length; i++) {
      const prev = coords[i - 1];
      const cur = coords[i];
      const dx = (cur[1] - prev[1]);
      const dy = (cur[0] - prev[0]);
      cum += Math.hypot(dx, dy);
      x.push(cum);
    }

    return { x, y };
  }

  return (
    <div className="hud-container">
      
      <div className="hud-header">
        <div className="header-left">
          <h1>LUNAR<span style={{color:'#fff'}}>.OS</span></h1>
          <span className="subtext">ORBITAL RECONNAISSANCE // V24.2</span>
        </div>
        <div className="status-badge">
          <span className="blink">●</span> {loading ? "SCANNING..." : "ONLINE"}
        </div>
      </div>

      <div className="mobile-tabs">
        <button className={activeTab === 'flight' ? 'active' : ''} onClick={() => setActiveTab('flight')}>DECK</button>
        <button className={activeTab === 'terrain' ? 'active' : ''} onClick={() => setActiveTab('terrain')}>TERRAIN</button>
        <button className={activeTab === 'analytics' ? 'active' : ''} onClick={() => setActiveTab('analytics')}>DATA</button>
        <button className={activeTab === 'physics' ? 'active' : ''} onClick={() => setActiveTab('physics')}>RISK</button>
      </div>

      <div className="grid-layout">
        
        {/* LEFT PANEL */}
        <div className={`panel col-left mobile-panel ${activeTab === 'flight' ? 'mobile-active' : ''}`}>
          <h3>FLIGHT_DECK</h3>
          <div className="control-group">
            <label>SECTOR_ID</label>
            <div className="input-row">
                <input type="number" className="tech-input" value={sectorId} onChange={(e) => setSectorId(e.target.value)} />
                <button className="scan-btn" onClick={handleScan} disabled={loading}>SCAN</button>
            </div>
          </div>
          <div className="divider"></div>
          
          {data ? (
            <div className="metrics-compact">
              <div className="m-row"><span>VEL:</span> <span className="val">{data.metrics.velocity}</span></div>
              <div className="m-row"><span>ALT:</span> <span className="val">{data.metrics.altitude}</span></div>
              <div className="m-row"><span>FUEL:</span> <span className="val text-green">{data.metrics.fuel_cost}</span></div>
            </div>
          ) : <p className="console-text">NO DATA LINK</p>}
          
          <div className="divider"></div>
          
          <h3>OPTICAL_FEED</h3>
          <div className="optical-box">
             {data ? (
                <img 
                    src={`data:image/png;base64,${showGroundTruth ? data.ground_truth : data.optical_feed}`} 
                    alt="Optical" 
                />
             ) : ( <div className="placeholder-scan">NO SIGNAL</div> )}
             
             <div className="overlay-label">
                {showGroundTruth ? "MODE: GROUND_TRUTH [REF]" : "MODE: LIVE_RECONSTRUCTION [AI]"}
             </div>

             {data && (
                 <button 
                    onClick={() => setShowGroundTruth(!showGroundTruth)}
                    style={{
                        position: 'absolute', bottom: 5, right: 5,
                        background: showGroundTruth ? '#FF4500' : 'rgba(0, 240, 255, 0.2)',
                        border: '1px solid #00F0FF', color: '#fff',
                        fontSize: '0.6rem', cursor: 'pointer', padding: '2px 5px',
                        fontFamily: 'Share Tech Mono', zIndex: 20
                    }}
                 >
                    {showGroundTruth ? "VIEW AI OUTPUT" : "VIEW GROUND TRUTH"}
                 </button>
             )}
          </div>
        </div>

        {/* CENTER PANEL */}
        <div className="col-center-container">
            <div className={`panel center-top mobile-panel ${activeTab === 'terrain' ? 'mobile-active' : ''}`}>
                <div className="ar-overlay">
                    <div className="bracket top-left"></div>
                    <div className="bracket top-right"></div>
                    <div className="bracket bottom-left"></div>
                    <div className="bracket bottom-right"></div>
                    <div className="center-reticle">+</div>
                </div>
                <div className="plot-wrapper">
                    <Plot
                    data={[
                        {
                        z: getTerrainData(),
                        type: 'surface',
                        colorscale: 'Cividis',
                        contours: { z: { show: true, usecolormap: true, highlightcolor: "#00F0FF", project: { z: true } } },
                        lighting: { ambient: 0.4, roughness: 0.9, diffuse: 0.5, fresnel: 0.5 },
                        opacity: 1.0,
                        name: 'Terrain'
                        },
                        pathTrace, roverTrace
                    ]}
                    layout={{
                        autosize: true,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        margin: {l:0, r:0, b:0, t:0},
                        showlegend: false,
                        scene: {
                            xaxis: {visible: false}, yaxis: {visible: false}, zaxis: {visible: false},
                            camera: { eye: {x:0.9, y:0.9, z:0.5}, center: {x:0, y:0, z:-0.1} },
                            aspectmode: 'manual', aspectratio: {x:1, y:1, z:0.08},
                            bgcolor: 'rgba(0,0,0,0)' 
                        },
                        updatemenus: [{
                            type: 'buttons', showactive: false,
                            x: 0.0, y: 0.95, xanchor: 'left', yanchor: 'top', 
                            pad: {t: 0, r: 10},
                            buttons: [{ label: '▶ INITIATE DRIVE', method: 'animate', args: [null, {frame: {duration: 50, redraw: true}, fromcurrent: true}] }],
                            bgcolor: "rgba(0, 240, 255, 0.1)",
                            font: { color: "#00F0FF" },
                            bordercolor: "#00F0FF", borderwidth: 1
                        }]
                    }}
                    frames={frames}
                    useResizeHandler={true}
                    style={{width: "100%", height: "100%"}}
                    config={{displayModeBar: false}}
                    />
                </div>
                <div className="panel-footer">LIDAR_TOPOGRAPHY_3D // REAL-TIME RENDERING</div>
            </div>

            <div className={`panel center-bottom mobile-panel ${activeTab === 'analytics' ? 'mobile-active' : ''}`}>
                <h3>MISSION ANALYTICS</h3>
                {data ? (
                    <div className="analytics-grid">
                        <div className="stats-box">
                            <div className="stat-item"><span className="lbl">DISTANCE</span><span className="val">{data.metrics.distance}</span></div>
                            <div className="stat-item"><span className="lbl">GRADIENT</span><span className="val text-red">42%</span></div>
                            <div className="stat-item"><span className="lbl">SAFETY</span><span className="val text-green">{data.metrics.safety}</span></div>
                        </div>

                        <div className="graph-box">
                            <div className="overlay-label">ELEVATION PROFILE</div>
                            <Plot 
                                data={[{
                                    x: getGraphData().x, 
                                    y: getGraphData().y,
                                    type: 'scatter', 
                                    mode: 'lines', 
                                    fill: 'tozeroy',
                                    line: {color: '#00F0FF', width: 2}
                                }]}
                                layout={{
                                    autosize: true, 
                                    margin: {l:25, r:10, t:10, b:20},
                                    paper_bgcolor: 'rgba(0,0,0,0)', 
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    xaxis: {showgrid: false, zeroline: false, color: '#555'},
                                    yaxis: {showgrid: true, gridcolor: '#222', color: '#555'}
                                }}
                                style={{width: "100%", height: "100%"}}
                                config={{displayModeBar: false}}
                            />
                        </div>

                        <div className="graph-box">
                            <div className="overlay-label">SECTOR COMP</div>
                             <Plot 
                                data={[{
                                    values: [data.sector_stats.safe, data.sector_stats.caution, data.sector_stats.danger], 
                                    labels: ['Safe', 'Caution', 'Hazard'],
                                    type: 'pie', hole: 0.6,
                                    marker: {colors: ['#00FF00', '#FFA500', '#FF0000']},
                                    textinfo: 'none'
                                }]}
                                layout={{
                                    autosize: true, margin: {l:10, r:10, t:10, b:10},
                                    paper_bgcolor: 'rgba(0,0,0,0)', showlegend: false
                                }}
                                style={{width: "100%", height: "100%"}}
                                config={{displayModeBar: false}}
                            />
                        </div>
                    </div>
                ) : <p className="console-text">WAITING FOR SCAN...</p>}
            </div>
        </div>

        {/* RIGHT PANEL */}
        <div className={`panel col-right mobile-panel ${activeTab === 'physics' ? 'mobile-active' : ''}`}>
          <h3>PHYSICS_ENGINE</h3>
          <div className="radar-box">
            <div className="radar-container">
              {data ? (
                <img src={`data:image/png;base64,${data.heatmap}`} className="heatmap-img" alt="Radar" />
              ) : ( <div className="heatmap-placeholder"></div> )} 
              <div className="radar-sweep"></div>
            </div>
            <div className="overlay-label">RISK_SCOPE</div>
          </div>
          <div className="divider"></div>
          <h3>SYS_LOGS</h3>
          <div className="console-box">
             <p>{'>'} A* SOLVER..... ACTIVE</p>
             <p>{'>'} PHYSICS ENG... READY</p>
             <p>{'>'} GRADIENT...... CALC</p>
             <p className="text-green">{'>'} UPLINK....... SECURE</p>
          </div>
        </div>

      </div>
    </div>
  )
}

export default App