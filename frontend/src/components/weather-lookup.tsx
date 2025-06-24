"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export function WeatherLookup() {
  const [weatherId, setWeatherId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  const handleFetch = async () => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`http://localhost:8000/weather/${weatherId}`);
      if (!res.ok) {
        const err = await res.json();
        setError(err.detail || "Not found");
      } else {
        const result = await res.json();
        setData(result);
      }
    } catch {
      setError("Network error: Could not connect to the server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Lookup Weather Data by ID</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-4">
          <Input
            placeholder="Enter weather data ID"
            value={weatherId}
            onChange={e => setWeatherId(e.target.value)}
            disabled={loading}
          />
          <Button onClick={handleFetch} disabled={loading || !weatherId}>
            {loading ? "Loading..." : "Lookup"}
          </Button>
        </div>
        {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
        {data && (
          <div className="text-sm space-y-2">
            <div>
              <span className="font-semibold">ID:</span> {data.id}
            </div>
            <div>
              <span className="font-semibold">Date:</span> {data.request_data?.date}
            </div>
            <div>
              <span className="font-semibold">Location:</span> {data.request_data?.location}
            </div>
            <div>
              <span className="font-semibold">Notes:</span> {data.request_data?.notes || "-"}
            </div>
            <div>
              <span className="font-semibold">Weather:</span>
              <ul className="ml-4 list-disc">
                <li>
                  <span className="font-semibold">Temperature:</span> {data.weather_data?.current?.temperature}°C
                </li>
                <li>
                  <span className="font-semibold">Description:</span> {data.weather_data?.current?.weather_descriptions?.join(", ")}
                </li>
                <li>
                  <span className="font-semibold">Humidity:</span> {data.weather_data?.current?.humidity}%
                </li>
                <li>
                  <span className="font-semibold">Wind:</span> {data.weather_data?.current?.wind_speed} km/h {data.weather_data?.current?.wind_dir}
                </li>
              </ul>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 