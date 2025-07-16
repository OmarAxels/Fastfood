'use client';

import React, { useState } from 'react';

export default function TestLLMFoodExtractorPage() {
  const [offerName, setOfferName] = useState('');
  const [description, setDescription] = useState('');
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    setLoading(true);
    setError(null);
    setResult('');
    try {
      const res = await fetch('http://localhost:8000/test/llm_food_extractor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ offer_name: offerName, description }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-300 p-6">
      <div className="max-w-xl mx-auto bg-white rounded-xl shadow-lg p-6">
        <h1 className="text-2xl font-bold mb-4">Test LLM Food Extractor</h1>
        <div className="mb-4">
          <label className="block font-semibold mb-1">Offer Name</label>
          <input
            className="w-full border rounded px-3 py-2 mb-2"
            value={offerName}
            onChange={e => setOfferName(e.target.value)}
            placeholder="e.g. Fjölskyldutilboð"
          />
          <label className="block font-semibold mb-1">Description</label>
          <textarea
            className="w-full border rounded px-3 py-2"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="e.g. 2 Búlluborgarar, 2 barnaborgarar, stór franskar, 2 l gos og 2 kokteilsósur"
            rows={3}
          />
        </div>
        <button
          className="bg-blue-600 text-white px-6 py-2 rounded font-semibold hover:bg-blue-700 transition-colors"
          onClick={handleTest}
          disabled={loading || !offerName}
        >
          {loading ? 'Running...' : 'Run LLM Food Extractor'}
        </button>
        <div className="mt-6">
          {error && <div className="text-red-500 mb-2">{error}</div>}
          {result && (
            <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto whitespace-pre-wrap break-all">{result}</pre>
          )}
        </div>
      </div>
    </div>
  );
} 