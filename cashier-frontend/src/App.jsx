import React, { useState } from 'react';
import './App.css';
import { REGULATIONS } from './constants/regulations';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [useBackend, setUseBackend] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setStatus('processing');

    if (useBackend) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('http://localhost:8000/api/v1/analyze', {
          method: 'POST',
          body: formData,
        });
        if (!response.ok) throw new Error('Ошибка сервера');
        const data = await response.json();
        setResult(data);
        setStatus('done');
      } catch (err) {
        console.error(err);
        setStatus('error');
      }
    } else {
      setTimeout(() => {
        setStatus('done');
        const violationKey = "V04"; 
        const regInfo = REGULATIONS[violationKey];

        setResult({
          job_id: "forte_datathon_2026_demo",
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
              evidence_frame: "https://images.unsplash.com/photo-1556742049-0a67d5e2c56f?auto=format&fit=crop&w=800&q=80"
            }
          ]
        });
      }, 2000);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Хэдер с вашим фоном и названием команды */}
      <div className="forte-navbar">
        <div className="forte-logo-area">
          <div className="forte-logo">forte</div>
          <span style={{ fontWeight: '600', color: '#374151', fontSize: '15px' }}>| Datathon 2026</span>
        </div>
        <div className="team-badge">
          🔥 Team: Hot Asian Chisks
        </div>
      </div>

      <div className="app-container">
        {/* Герой-баннер */}
        <div className="hero-banner">
          <div>
            <h1>Контроль кассовых операций</h1>
            <p>Автоматизированная проверка видеопотоков на соответствие стандартам и законам РК</p>
          </div>
        </div>

        {/* Основная рабочая панель */}
        <div className="main-card">
          <div style={{ marginBottom: '20px', fontSize: '14px', color: '#4b5563' }}>
            <label style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
              <input 
                type="checkbox" 
                checked={useBackend} 
                onChange={(e) => setUseBackend(e.target.checked)} 
              />
              <b>Подключить реальный FastAPI бэкенд</b> (порт 8000)
            </label>
          </div>

          <div className="upload-zone" onClick={() => document.getElementById('fileInput').click()}>
            <input 
              id="fileInput"
              type="file" 
              accept=".mov,video/quicktime,video/mp4" 
              onChange={handleFileChange} 
              style={{ display: 'none' }}
            />
            <p style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: '600', color: '#1f2937' }}>
              {file ? `📁 Выбран файл: ${file.name}` : '📥 Перетащите видеозапись (.mov / .mp4) сюда'}
            </p>
            <span style={{ color: '#6b7280', fontSize: '13px' }}>Поддерживается проверка датасета инвентаря касс</span>
          </div>

          <button 
            className="btn-forte"
            onClick={handleAnalyze} 
            disabled={!file || status === 'processing'}
          >
            {status === 'processing' ? '⏳ Выполняется покадровый анализ...' : 'Запустить проверку соблюдения правил'}
          </button>

          {status === 'error' && (
            <div style={{ marginTop: '20px', padding: '15px', background: '#fee2e2', color: '#991b1b', borderRadius: '8px' }}>
              ❌ Ошибка подключения к бэкенду. Проверьте запуск сервера FastAPI.
            </div>
          )}

          {status === 'done' && result && (
            <div style={{ marginTop: '30px', borderTop: '1px solid var(--border-color)', paddingTop: '25px' }}>
              <h3 style={{ margin: '0 0 20px 0', fontSize: '20px' }}>Экспертное заключение:</h3>
              
              {result.verdict === 'no_violation' ? (
                <div className="success-alert">
                  ✅ Нарушений кассовой дисциплины не зафиксировано.
                </div>
              ) : (
                <>
                  <div className="violation-alert">
                    ⚠️ Внимание: Зафиксировано отклонение от регламента кассовых операций
                  </div>

                  {result.violations && result.violations.map((item, index) => (
                    <div key={index} className="result-card">
                      <h4 style={{ margin: '0 0 10px 0', color: 'var(--forte-burgundy)', fontSize: '18px' }}>
                        {item.violation_id ? `[${item.violation_id}] ` : ''}{item.type}
                      </h4>
                      <p style={{ margin: '6px 0' }}><b>Таймкод на видео:</b> <span style={{ color: 'var(--forte-burgundy)', fontWeight: '600' }}>{item.timecode_sec} сек</span></p>
                      <p style={{ margin: '6px 0 15px 0' }}><b>Описание события:</b> {item.description}</p>
                      
                      {item.regulatory_reference && (
                        <div className="reg-box">
                          <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}><b>Правовое обоснование РК (adilet.zan.kz):</b></p>
                          <p style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#1f2937' }}><b>{item.regulatory_reference.document}</b></p>
                          <p style={{ margin: '0 0 5px 0', fontSize: '14px', color: 'var(--forte-burgundy)' }}><i>{item.regulatory_reference.clause}</i></p>
                          <p style={{ margin: 0, fontSize: '13px', color: '#4b5563' }}>{item.regulatory_reference.details || item.regulatory_reference.description}</p>
                        </div>
                      )}

                      {item.evidence_frame && (
                        <div style={{ marginTop: '15px' }}>
                          <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '6px' }}><b>Кадр-фиксация нарушения:</b></p>
                          <img src={item.evidence_frame} alt="Evidence" className="evidence-img" />
                        </div>
                      )}
                    </div>
                  ))}
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Футер с именами и командой */}
      <footer className="forte-footer">
        <div className="footer-content">
          <div><b>ForteBank Datathon 2026</b> • Командный проект</div>
          <div className="team-members">
            Разработано командой <b>Hot Asian Chisks</b>: Kamila A. | Begina M. | Ayganym B. | Assel T.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;