import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, done, failed
  const [result, setResult] = useState(null);

  // Обработка выбора файла
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // Отправка видео на бэкенд (или заглушка для теста)
  const handleAnalyze = async () => {
    if (!file) return;

    setStatus('processing');

    // ТУТ БУДЕТ ВАШ API-ЗАПРОС К PYTHON (FastAPI):
    // const formData = new FormData();
    // formData.append('file', file);
    // const res = await fetch('https://your-backend.kz/api/v1/analyze', {
    //   method: 'POST',
    //   headers: { 'X-API-Key': 'ваш_ключ' },
    //   body: formData
    // });
    // const data = await res.json();
    // const jobId = data.job_id;
    // ... опрос статуса GET /api/v1/jobs/{job_id} ...

    // ДЛЯ ТЕСТА (мокаем ответ через 3 секунды):
    setTimeout(() => {
      setStatus('done');
      setResult({
        job_id: "forte_demo_01",
        verdict: "violation", // или "no_violation"
        violations: [
          {
            type: "Оставление рабочего места кассиром",
            timecode_sec: 22.0,
            description: "На видео зафиксировано, как кассир покидает рабочее место до завершения расчетной операции, оставляя зону без контроля.",
            evidence_frames: [
              { timestamp_sec: 22.0, image_base64: "https://via.placeholder.com/300x169.png?text=Evidence+Frame+22s" }
            ],
            regulatory_reference: {
              document: "Правила ведения кассовых операций в банках Республики Казахстан (adilet.zan.kz)",
              clause: "Пункт 22"
            }
          }
        ]
      });
    }, 3000);
  };

  return (
    <div style={{ padding: '30px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>ForteBank Datathon 26 — Контроль кассовой дисциплины</h2>
      <p>Загрузите видеозапись (.mov) для проверки на видимые признаки нарушений.</p>

      {/* Зона загрузки */}
      <div style={{ border: '2px dashed #ccc', padding: '20px', textAlign: 'center', marginBottom: '20px', borderRadius: '8px' }}>
        <input type="file" accept=".mov,video/quicktime" onChange={handleFileChange} />
        {file && <p>Выбран файл: <b>{file.name}</b> ({(file.size / (1024*1024)).toFixed(2)} MB)</p>}
      </div>

      <button 
        onClick={handleAnalyze} 
        disabled={!file || status === 'processing'}
        style={{ padding: '10px 20px', fontSize: '16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
      >
        {status === 'processing' ? 'Анализ видео (может занять до 5 минут)...' : 'Запустить анализ'}
      </button>

      {/* Статус обработки */}
      {status === 'processing' && (
        <div style={{ marginTop: '20px', color: '#ff8c00' }}>
          ⏳ Идет обработка видеокадров и сверка с нормативной базой РК...
        </div>
      )}

      {/* Результаты */}
      {status === 'done' && result && (
        <div style={{ marginTop: '30px', borderTop: '1px solid #ddd', paddingTop: '20px' }}>
          <h3>Результат проверки:</h3>
          <div style={{ 
            padding: '15px', 
            borderRadius: '6px', 
            background: result.verdict === 'violation' ? '#ffe6e6' : '#e6ffe6',
            color: result.verdict === 'violation' ? '#d9534f' : '#28a745',
            fontWeight: 'bold',
            fontSize: '18px',
            marginBottom: '20px'
          }}>
            {result.verdict === 'violation' ? '⚠️ Обнаружены признаки возможных нарушений' : '✅ Нарушение не обнаружено'}
          </div>

          {result.violations && result.violations.map((item, index) => (
            <div key={index} style={{ background: '#f9f9f9', padding: '15px', borderRadius: '6px', marginBottom: '15px', border: '1px solid #eee' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>{item.type}</h4>
              <p><b>Таймкод:</b> <span style={{ color: '#007bff', cursor: 'pointer' }}>{item.timecode_sec} сек</span></p>
              <p><b>Описание:</b> {item.description}</p>
              
              <div style={{ background: '#fff', padding: '10px', border: '1px solid #ddd', borderRadius: '4px', marginBottom: '10px' }}>
                <p style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#666' }}><b>Нормативный источник РК:</b></p>
                <p style={{ margin: 0, fontSize: '14px' }}>📜 {item.regulatory_reference.document} ({item.regulatory_reference.clause})</p>
              </div>

              <div>
                <p style={{ fontSize: '14px', color: '#666' }}><b>Кадр-доказательство:</b></p>
                {item.evidence_frames.map((frame, fIdx) => (
                  <img 
                    key={fIdx} 
                    src={frame.image_base64} 
                    alt="Evidence" 
                    style={{ maxWidth: '100%', borderRadius: '4px', border: '1px solid #ccc' }} 
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;