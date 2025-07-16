import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { promises as fs } from 'fs';

export async function POST(req: Request) {
  try {
    const { offer_name, description } = await req.json();
    
    // Prepare the offer as a single-item batch
    const offer = {
      offer_name,
      description,
      price_kr: null,
      pickup_delivery: null,
      suits_people: null,
      available_weekdays: null,
      available_hours: null,
      restaurant_name: 'Test'
    };
    
    // Fix path resolution - from frontend to scraper
    const scriptPath = path.resolve(process.cwd(), '..', 'scraper', 'src', 'llm_food_extractor_cli.py');
    
    // Check if file exists
    try {
      await fs.access(scriptPath);
    } catch {
      return NextResponse.json({ 
        error: `Python script not found at: ${scriptPath}`,
        cwd: process.cwd()
      }, { status: 500 });
    }
    
    const offersJson = JSON.stringify([offer]);

    return await new Promise((resolve) => {
      // Try different Python commands
      const pythonCommands = ['python', 'python3', 'py'];
      let pythonCmd = 'python';
      
      const py = spawn(pythonCmd, [scriptPath], { 
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.dirname(scriptPath) // Set working directory to script location
      });
      
      let output = '';
      let error = '';
      
      py.stdout.on('data', (data) => { output += data.toString(); });
      py.stderr.on('data', (data) => { error += data.toString(); });
      
      py.on('close', (code) => {
        if (code !== 0 || error) {
          resolve(NextResponse.json({ 
            error: error || `Python exited with code ${code}`,
            scriptPath,
            output: output || 'No output'
          }, { status: 500 }));
        } else {
          try {
            // Expect output to be a JSON array
            const arr = JSON.parse(output);
            resolve(NextResponse.json(arr[0] || {}));
          } catch (e: any) {
            resolve(NextResponse.json({ 
              error: 'Failed to parse Python output', 
              details: output,
              parseError: e.message
            }, { status: 500 }));
          }
        }
      });
      
      py.stdin.write(offersJson);
      py.stdin.end();
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
} 