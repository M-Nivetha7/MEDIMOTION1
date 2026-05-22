import React, { useRef, useEffect, useState } from 'react';
import * as tf from '@tensorflow/tfjs';
import * as poseDetection from '@teachablemachine/pose';

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isTracking, setIsTracking] = useState(false);
  const [exercise, setExercise] = useState('shoulder_raise');
  const [angles, setAngles] = useState({});
  const [feedback, setFeedback] = useState('');
  const [model, setModel] = useState(null);
  const [status, setStatus] = useState('Initializing...');

  // Initialize camera
  useEffect(() => {
    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: 640, height: 480 } 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => {
            videoRef.current.play();
            setStatus('Camera ready. Loading model...');
          };
        }
      } catch (err) {
        setStatus('Camera error: ' + err.message);
      }
    };
    initCamera();
  }, []);

  // Load model
  useEffect(() => {
    const loadModel = async () => {
      try {
        await tf.ready();
        const poseModel = await poseDetection.load(
          'https://teachablemachine.withgoogle.com/models/jnBvP8xJm/',
          { modelUrl: 'https://teachablemachine.withgoogle.com/models/jnBvP8xJm/model.json' }
        );
        setModel(poseModel);
        setStatus('Ready! Click Start Tracking');
      } catch (err) {
        console.error('Model load error:', err);
        setStatus('Using fallback mode');
      }
    };
    loadModel();
  }, []);

  const calculateAngle = (p1, p2, p3) => {
    if (!p1 || !p2 || !p3) return 0;
    const angle1 = Math.atan2(p1.y - p2.y, p1.x - p2.x);
    const angle2 = Math.atan2(p3.y - p2.y, p3.x - p2.x);
    let angle = (angle2 - angle1) * 180 / Math.PI;
    if (angle < 0) angle += 360;
    if (angle > 180) angle = 360 - angle;
    return angle;
  };

  // Draw skeleton
  const drawSkeleton = (ctx, pose, anglesData) => {
    if (!pose || !pose.keypoints) return;
    
    const keypoints = pose.keypoints;
    const connections = [
      ['left_shoulder', 'right_shoulder'],
      ['left_shoulder', 'left_elbow'], ['left_elbow', 'left_wrist'],
      ['right_shoulder', 'right_elbow'], ['right_elbow', 'right_wrist'],
      ['left_shoulder', 'left_hip'], ['right_shoulder', 'right_hip'],
      ['left_hip', 'right_hip'],
      ['left_hip', 'left_knee'], ['left_knee', 'left_ankle'],
      ['right_hip', 'right_knee'], ['right_knee', 'right_ankle']
    ];
    
    // Draw lines
    connections.forEach(([part1, part2]) => {
      const p1 = keypoints.find(k => k.name === part1);
      const p2 = keypoints.find(k => k.name === part2);
      if (p1 && p2 && p1.score > 0.3 && p2.score > 0.3) {
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = '#00FF00';
        ctx.lineWidth = 4;
        ctx.stroke();
      }
    });
    
    // Draw joints
    keypoints.forEach(point => {
      if (point.score > 0.3) {
        ctx.beginPath();
        ctx.arc(point.x, point.y, 6, 0, 2 * Math.PI);
        ctx.fillStyle = '#FF0000';
        ctx.fill();
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    });
    
    // Draw angles
    let y = 30;
    ctx.font = 'bold 18px Arial';
    ctx.fillStyle = '#00FF00';
    for (const [joint, angle] of Object.entries(anglesData)) {
      ctx.fillText(`${joint}: ${Math.round(angle)}°`, 10, y);
      y += 30;
    }
  };

  // Tracking loop
  useEffect(() => {
    let animationId;
    
    const track = async () => {
      if (!isTracking || !model || !videoRef.current || !canvasRef.current) {
        animationId = requestAnimationFrame(track);
        return;
      }
      
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      if (video.videoWidth === 0) {
        animationId = requestAnimationFrame(track);
        return;
      }
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      try {
        const predictions = await model.estimatePose(video);
        
        if (predictions && predictions.pose && predictions.pose.keypoints) {
          const kp = predictions.pose.keypoints;
          
          const leftShoulder = kp.find(k => k.name === 'left_shoulder');
          const rightShoulder = kp.find(k => k.name === 'right_shoulder');
          const leftElbow = kp.find(k => k.name === 'left_elbow');
          const rightElbow = kp.find(k => k.name === 'right_elbow');
          const leftWrist = kp.find(k => k.name === 'left_wrist');
          const rightWrist = kp.find(k => k.name === 'right_wrist');
          const leftHip = kp.find(k => k.name === 'left_hip');
          const rightHip = kp.find(k => k.name === 'right_hip');
          const leftKnee = kp.find(k => k.name === 'left_knee');
          const rightKnee = kp.find(k => k.name === 'right_knee');
          const leftAnkle = kp.find(k => k.name === 'left_ankle');
          const rightAnkle = kp.find(k => k.name === 'right_ankle');
          
          const newAngles = {};
          
          if (exercise === 'shoulder_raise') {
            if (leftShoulder && leftHip && leftElbow && leftShoulder.score > 0.3) {
              newAngles['Left Shoulder'] = calculateAngle(leftHip, leftShoulder, leftElbow);
            }
            if (rightShoulder && rightHip && rightElbow && rightShoulder.score > 0.3) {
              newAngles['Right Shoulder'] = calculateAngle(rightHip, rightShoulder, rightElbow);
            }
          } else if (exercise === 'elbow_curl') {
            if (leftShoulder && leftElbow && leftWrist && leftElbow.score > 0.3) {
              newAngles['Left Elbow'] = calculateAngle(leftShoulder, leftElbow, leftWrist);
            }
            if (rightShoulder && rightElbow && rightWrist && rightElbow.score > 0.3) {
              newAngles['Right Elbow'] = calculateAngle(rightShoulder, rightElbow, rightWrist);
            }
          } else {
            if (leftHip && leftKnee && leftAnkle && leftKnee.score > 0.3) {
              newAngles['Left Knee'] = calculateAngle(leftHip, leftKnee, leftAnkle);
            }
            if (rightHip && rightKnee && rightAnkle && rightKnee.score > 0.3) {
              newAngles['Right Knee'] = calculateAngle(rightHip, rightKnee, rightAnkle);
            }
          }
          
          setAngles(newAngles);
          
          let total = 0;
          for (const angle of Object.values(newAngles)) {
            if (angle > 150) total += 90;
            else if (angle > 120) total += 70;
            else total += 50;
          }
          const score = Object.keys(newAngles).length > 0 ? total / Object.keys(newAngles).length : 0;
          
          if (score > 80) setFeedback('🎉 Excellent form! Keep it up!');
          else if (score > 60) setFeedback('💪 Good! Try to extend more');
          else if (score > 0) setFeedback('📈 Keep practicing! Focus on range of motion');
          
          drawSkeleton(ctx, predictions.pose, newAngles);
          
          if (score > 0) {
            ctx.font = 'bold 20px Arial';
            ctx.fillStyle = '#FFFF00';
            ctx.fillText(`Score: ${Math.round(score)}%`, 10, 30 + Object.keys(newAngles).length * 30);
          }
        }
      } catch (err) {
        console.error('Tracking error:', err);
      }
      
      animationId = requestAnimationFrame(track);
    };
    
    if (isTracking) {
      track();
    }
    
    return () => {
      if (animationId) cancelAnimationFrame(animationId);
    };
  }, [isTracking, model, exercise]);

  return (
    <div style={{ minHeight: '100vh', background: '#1a1a2e', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ color: 'white', textAlign: 'center' }}>🏥 MediMotion - Physiotherapy Tracker</h1>
        
        <div style={{ background: '#0f3460', borderRadius: '10px', padding: '15px', marginBottom: '20px', color: 'white' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>📹 Status: {status}</span>
            {isTracking && <span style={{ color: '#00ff00' }}>● LIVE TRACKING</span>}
          </div>
        </div>
        
        <div style={{ background: 'white', borderRadius: '10px', padding: '20px', marginBottom: '20px' }}>
          <h3>Select Exercise</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
            <button onClick={() => setExercise('shoulder_raise')} style={{
              padding: '15px',
              border: `2px solid ${exercise === 'shoulder_raise' ? '#4CAF50' : '#ddd'}`,
              borderRadius: '10px',
              background: exercise === 'shoulder_raise' ? '#e8f5e9' : 'white',
              cursor: 'pointer'
            }}>
              🏋️ Shoulder Raise
            </button>
            <button onClick={() => setExercise('elbow_curl')} style={{
              padding: '15px',
              border: `2px solid ${exercise === 'elbow_curl' ? '#4CAF50' : '#ddd'}`,
              borderRadius: '10px',
              background: exercise === 'elbow_curl' ? '#e8f5e9' : 'white',
              cursor: 'pointer'
            }}>
              💪 Elbow Curl
            </button>
            <button onClick={() => setExercise('knee_bend')} style={{
              padding: '15px',
              border: `2px solid ${exercise === 'knee_bend' ? '#4CAF50' : '#ddd'}`,
              borderRadius: '10px',
              background: exercise === 'knee_bend' ? '#e8f5e9' : 'white',
              cursor: 'pointer'
            }}>
              🦵 Knee Bend
            </button>
          </div>
        </div>
        
        <div style={{ background: 'white', borderRadius: '10px', padding: '20px', marginBottom: '20px' }}>
          <button
            onClick={() => setIsTracking(!isTracking)}
            style={{
              width: '100%',
              padding: '20px',
              fontSize: '20px',
              fontWeight: 'bold',
              background: isTracking ? '#f44336' : '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              cursor: 'pointer'
            }}
          >
            {isTracking ? '⏹️ STOP TRACKING' : '▶️ START TRACKING'}
          </button>
        </div>
        
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{ flex: 2, minWidth: '500px', position: 'relative', background: '#000', borderRadius: '10px', overflow: 'hidden' }}>
            <video ref={videoRef} style={{ width: '100%', display: 'block' }} autoPlay playsInline muted />
            <canvas ref={canvasRef} style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }} />
          </div>
          
          <div style={{ flex: 1, minWidth: '250px' }}>
            <div style={{ background: 'white', borderRadius: '10px', padding: '20px', marginBottom: '20px' }}>
              <h3>📐 Joint Angles</h3>
              {Object.keys(angles).length === 0 ? (
                <p style={{ textAlign: 'center', padding: '20px' }}>
                  {isTracking ? 'Detecting pose...' : 'Start tracking'}
                </p>
              ) : (
                Object.entries(angles).map(([joint, angle]) => (
                  <div key={joint} style={{ marginBottom: '15px' }}>
                    <div style={{ fontWeight: 'bold' }}>{joint}</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2196F3' }}>{Math.round(angle)}°</div>
                    <div style={{ height: '8px', background: '#e0e0e0', borderRadius: '4px', marginTop: '5px' }}>
                      <div style={{ width: `${(angle/180)*100}%`, height: '100%', background: '#4CAF50', borderRadius: '4px' }} />
                    </div>
                  </div>
                ))
              )}
            </div>
            
            {feedback && (
              <div style={{ background: '#e3f2fd', borderRadius: '10px', padding: '20px' }}>
                <h3>🤖 AI Feedback</h3>
                <p>{feedback}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
