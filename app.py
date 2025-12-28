import React, { useState, useRef } from ‘react’;
import { Camera, Upload, X, FileText, AlertCircle, CheckCircle } from ‘lucide-react’;

export default function ECGAnalyzer() {
const [image, setImage] = useState(null);
const [fileName, setFileName] = useState(’’);
const [analysis, setAnalysis] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(’’);
const fileInputRef = useRef(null);
const cameraInputRef = useRef(null);

const handleImageUpload = (e) => {
const file = e.target.files && e.target.files[0];
if (!file) {
console.log(‘No file selected’);
return;
}

```
console.log('File selected:', file.name, file.type);
setError('');
setFileName(file.name);

// Handle PDF files
if (file.type === 'application/pdf') {
  setImage('pdf');
  setAnalysis(null);
  return;
}

// Handle image files (JPG, JPEG, PNG)
const reader = new FileReader();

reader.onload = (event) => {
  console.log('File loaded successfully');
  setImage(event.target.result);
  setAnalysis(null);
};

reader.onerror = (error) => {
  console.error('FileReader error:', error);
  setError('Failed to read file. Please try again.');
};

reader.readAsDataURL(file);
```

};

const analyzeECG = () => {
setLoading(true);

```
// Simulate analysis based on the workflow
setTimeout(() => {
  const mockAnalysis = {
    rhythm: {
      regular: true,
      rate: 75,
      pWaves: "Present before each QRS",
      prInterval: 0.16,
      qrsWidth: 0.09
    },
    axis: {
      normal: true,
      degrees: 60,
      deviation: "Normal axis"
    },
    hypertrophy: {
      lvh: false,
      rvh: false,
      atrialEnlargement: false
    },
    infarction: {
      stemi: false,
      qWaves: false,
      tWaveInversion: false,
      stChanges: "No significant ST changes"
    },
    intervals: {
      qt: 0.40,
      qtc: 0.42,
      prolonged: false
    },
    interpretation: "Normal Sinus Rhythm",
    findings: [
      "Regular rhythm at 75 bpm",
      "Normal axis (60°)",
      "Normal QRS duration (0.09s)",
      "Normal PR interval (0.16s)",
      "Normal QTc interval",
      "No acute ST-T wave changes"
    ]
  };
  
  setAnalysis(mockAnalysis);
  setLoading(false);
}, 2000);
```

};

const clearImage = () => {
setImage(null);
setAnalysis(null);
setFileName(’’);
setError(’’);
};

const triggerFileInput = () => {
fileInputRef.current?.click();
};

const triggerCameraInput = () => {
cameraInputRef.current?.click();
};

return (
<div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
<div className="max-w-6xl mx-auto">
{/* Header */}
<div className="bg-white rounded-lg shadow-lg p-6 mb-6">
<h1 className="text-3xl font-bold text-gray-800 mb-2">ECG Analysis Tool</h1>
<p className="text-gray-600">Upload an ECG image for systematic analysis</p>
</div>

```
    {/* Error Message */}
    {error && (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    )}

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload ECG</h2>
        
        {!image ? (
          <div className="space-y-4">
            <button
              onClick={triggerCameraInput}
              className="w-full border-2 border-dashed border-blue-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition"
            >
              <Camera className="w-12 h-12 text-blue-500 mx-auto mb-3" />
              <p className="text-gray-700 font-medium">Take Photo</p>
              <p className="text-gray-500 text-sm">Use camera to capture ECG</p>
            </button>
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleImageUpload}
              style={{ display: 'none' }}
            />

            <button
              onClick={triggerFileInput}
              className="w-full border-2 border-dashed border-green-300 rounded-lg p-8 text-center cursor-pointer hover:border-green-500 hover:bg-green-50 transition"
            >
              <Upload className="w-12 h-12 text-green-500 mx-auto mb-3" />
              <p className="text-gray-700 font-medium">Upload File</p>
              <p className="text-gray-500 text-sm">JPG, JPEG, PNG, or PDF</p>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,application/pdf"
              onChange={handleImageUpload}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              {image === 'pdf' ? (
                <div className="w-full h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <FileText className="w-16 h-16 text-blue-500 mx-auto mb-3" />
                    <p className="text-gray-700 font-medium">PDF File Loaded</p>
                    <p className="text-gray-500 text-sm">{fileName}</p>
                  </div>
                </div>
              ) : (
                <img
                  src={image}
                  alt="ECG"
                  className="w-full h-64 object-contain bg-gray-100 rounded-lg"
                />
              )}
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition shadow-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            {fileName && (
              <div className="text-sm text-gray-600 text-center">
                <p className="truncate">📎 {fileName}</p>
              </div>
            )}
            
            <button
              onClick={analyzeECG}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 transition"
            >
              {loading ? 'Analyzing...' : 'Analyze ECG'}
            </button>

            <button
              onClick={clearImage}
              className="w-full bg-gray-200 text-gray-700 py-2 rounded-lg font-medium hover:bg-gray-300 transition"
            >
              Upload Different File
            </button>
          </div>
        )}
      </div>

      {/* Analysis Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Analysis Results</h2>
        
        {!analysis && !loading && (
          <div className="text-center py-12 text-gray-400">
            <FileText className="w-16 h-16 mx-auto mb-3" />
            <p>Upload an ECG to see analysis results</p>
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-3"></div>
            <p className="text-gray-600">Analyzing ECG...</p>
          </div>
        )}

        {analysis && (
          <div className="space-y-4 max-h-[600px] overflow-y-auto">
            {/* Interpretation */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-green-800">Interpretation</h3>
                  <p className="text-green-700">{analysis.interpretation}</p>
                </div>
              </div>
            </div>

            {/* Rhythm Analysis */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">1. Rhythm & Rate</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Regularity:</span>
                  <span className="font-medium">{analysis.rhythm.regular ? 'Regular' : 'Irregular'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Heart Rate:</span>
                  <span className="font-medium">{analysis.rhythm.rate} bpm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">P Waves:</span>
                  <span className="font-medium">{analysis.rhythm.pWaves}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">PR Interval:</span>
                  <span className="font-medium">{analysis.rhythm.prInterval}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">QRS Width:</span>
                  <span className="font-medium">{analysis.rhythm.qrsWidth}s</span>
                </div>
              </div>
            </div>

            {/* Axis */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">2. Axis</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Axis:</span>
                  <span className="font-medium">{analysis.axis.degrees}°</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Assessment:</span>
                  <span className="font-medium">{analysis.axis.deviation}</span>
                </div>
              </div>
            </div>

            {/* Intervals */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">3. Intervals</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">QT Interval:</span>
                  <span className="font-medium">{analysis.intervals.qt}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">QTc:</span>
                  <span className="font-medium">{analysis.intervals.qtc}s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="font-medium">{analysis.intervals.prolonged ? 'Prolonged' : 'Normal'}</span>
                </div>
              </div>
            </div>

            {/* Hypertrophy */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">4. Hypertrophy</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">LVH:</span>
                  <span className="font-medium">{analysis.hypertrophy.lvh ? 'Present' : 'Absent'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">RVH:</span>
                  <span className="font-medium">{analysis.hypertrophy.rvh ? 'Present' : 'Absent'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Atrial Enlargement:</span>
                  <span className="font-medium">{analysis.hypertrophy.atrialEnlargement ? 'Present' : 'Absent'}</span>
                </div>
              </div>
            </div>

            {/* Infarction */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">5. Infarction</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">STEMI:</span>
                  <span className="font-medium">{analysis.infarction.stemi ? 'Present' : 'Absent'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Q Waves:</span>
                  <span className="font-medium">{analysis.infarction.qWaves ? 'Pathological' : 'Normal'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">ST Changes:</span>
                  <span className="font-medium">{analysis.infarction.stChanges}</span>
                </div>
              </div>
            </div>

            {/* Key Findings */}
            <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800 mb-3">Key Findings</h3>
              <ul className="space-y-1 text-sm">
                {analysis.findings.map((finding, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span className="text-blue-700">{finding}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Disclaimer */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                <p className="text-yellow-800 text-xs">
                  <strong>Disclaimer:</strong> This is a demonstration tool only. 
                  ECG interpretation requires clinical expertise and should be performed 
                  by qualified healthcare professionals. Always seek professional medical 
                  advice for ECG analysis and diagnosis.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>

    {/* Workflow Reference */}
    <div className="bg-white rounded-lg shadow-lg p-6 mt-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">ECG Analysis Workflow</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div className="border border-gray-200 rounded p-3">
          <h3 className="font-semibold text-blue-600 mb-2">Step 1: Rhythm & Rate</h3>
          <p className="text-gray-600">Check regularity, calculate rate, assess P waves, PR interval, and QRS width</p>
        </div>
        <div className="border border-gray-200 rounded p-3">
          <h3 className="font-semibold text-blue-600 mb-2">Step 2: Axis</h3>
          <p className="text-gray-600">Determine cardiac axis using lead I and aVF</p>
        </div>
        <div className="border border-gray-200 rounded p-3">
          <h3 className="font-semibold text-blue-600 mb-2">Step 3: Intervals</h3>
          <p className="text-gray-600">Measure QT interval and calculate QTc</p>
        </div>
        <div className="border border-gray-200 rounded p-3">
          <h3 className="font-semibold text-blue-600 mb-2">Step 4: Hypertrophy</h3>
          <p className="text-gray-600">Look for LVH, RVH, and atrial enlargement</p>
        </div>
        <div className="border border-gray-200 rounded p-3">
          <h3 className="font-semibold text-blue-600 mb-2">Step 5: Infarction</h3>
          <p className="text-gray-600">Check for Q waves, ST changes, and T wave abnormalities</p>
        </div>
        <div className="border border-gray-200 rounded p-3">
          <h3 className="font-semibold text-blue-600 mb-2">Step 6: Summary</h3>
          <p className="text-gray-600">Synthesize findings into clinical interpretation</p>
        </div>
      </div>
    </div>
  </div>
</div>
```

);
}