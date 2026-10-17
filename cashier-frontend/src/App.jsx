import React, { useState } from 'react';
import './App.css';
import { REGULATIONS } from './constants/regulations';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, processing, done
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setStatus('processing');

    // Симуляция ответа бэкенда с привязкой к нашему ID нарушения (например, V04 - Оставленная активная кассовая программа)
    setTimeout(() => {
      setStatus('done');
      const violationKey = "V04"; 
      const regInfo = REGULATIONS[violationKey];

      setResult({
        job_id: "forte_datathon_2026",
        verdict: "violation",
        violations: [
          {
            type: regInfo.category,
            violation_id: violationKey,
            timecode_sec: "00:18",
            description: "На видео зафиксировано, как кассир оставил рабочее место с активной кассовой системой без блокировки.",
            regulatory_reference: {
              document: regInfo.document,
              clause: regInfo.clause,
              details: regInfo.description
            },
            evidence_frame: "https://via.placeholder.com/300x169.png?text=Evidence+00:18"
          }
        ]
      });
    }, 2500);
  };

  return (
    <div style={{ padding: '30px', maxWidth: '850px', margin: '0 auto', fontFamily: 'sans-serif', color: '#333' }}>
      <h2>ForteBank Datathon 26 — Контроль кассовой дисциплины</h2>
      <p>Локальный AI-сервис проверки видеозаписей на соответствие нормативам РК.</p>

      {/* Зона загрузки */}
      <div style={{ border: '2px dashed #007bff', padding: '25px', textAlign: 'center', marginBottom: '20px', borderRadius: '8px', background: '#f8f9fa' }}>
        <input type="file" accept=".mov,video/quicktime,video/mp4" onChange={handleFileChange} />
        {file && <p style={{ marginTop: '10px' }}>Выбран файл: <b>{file.name}</b></p>}
      </div>

      <button 
        onClick={handleAnalyze} 
        disabled={!file || status === 'processing'}
        style={{ padding: '12px 24px', fontSize: '16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
      >
        {status === 'processing' ? 'Анализ кадров и сверка с НБРК...' : 'Запустить анализ'}
      </button>

      {status === 'processing' && (
        <div style={{ marginTop: '20px', color: '#d9534f', fontWeight: 'bold' }}>
          ⏳ Выполняется покадровый анализ и поиск правовых оснований...
        </div>
      )}

      {status === 'done' && result && (
        <div style={{ marginTop: '30px', borderTop: '2px solid #eee', paddingTop: '20px' }}>
          <h3>Результат проверки:</h3>
          <div style={{ padding: '15px', borderRadius: '6px', background: '#ffe6e6', color: '#d9534f', fontWeight: 'bold', marginBottom: '20px' }}>
            ⚠️ Обнаружены нарушения кассовой дисциплины
          </div>

          {result.violations.map((item, index) => (
            <div key={index} style={{ background: '#fff', padding: '20px', borderRadius: '8px', marginBottom: '15px', border: '1px solid #ddd', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#007bff' }}>[{item.violation_id}] {item.type}</h4>
              <p><b>Таймкод:</b> {item.timecode_sec}</p>
              <p><b>Описание ситуации:</b> {item.description}</p>
              
              {/* Блок юридического обоснования РК */}
              <div style={{ background: '#e9ecef', padding: '12px', borderRadius: '6px', margin: '15px 0', borderLeft: '4px solid #007bff' }}>
                <p style={{ margin: '0 0 5px 0', fontSize: '14px' }}><b>📜 Нормативная база РК (adilet.zan.kz):</b></p>
                <p style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#004085' }}><b>{item.regulatory_reference.document}</b></p>
                <p style={{ margin: '0 0 5px 0', fontSize: '14px' }}><i>{item.regulatory_reference.clause}</i></p>
                <p style={{ margin: 0, fontSize: '13px', color: '#555' }}>{item.regulatory_reference.details}</p>
              </div>

              <div>
                <p style={{ fontSize: '14px', color: '#666' }}><b>Кадр-доказательство нарушения:</b></p>
                <img src={item.evidence_frame} alt="Evidence" style={{ maxWidth: '100%', borderRadius: '4px', border: '1px solid #ccc' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;