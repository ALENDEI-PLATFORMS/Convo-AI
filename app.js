const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const { PythonShell } = require('python-shell');

const app = express();
const port = 5001;

app.use(bodyParser.json());

app.post('/ask', async (req, res) => {
  try {
    const question = req.body.question;

    if (!question) {
      return res
        .status(400)
        .json({ error: 'Missing question in request body' });
    }

    const pythonProcess = spawn('python', ['./just_q&a.py', question]);

    let answer = '';
    pythonProcess.stdout.on('data', (data) => {
      answer += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Error from Python script: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python script exited with code: ${code}`);
        return res.status(500).json({ error: 'Internal server error' });
      }
      console.log(answer);
      res.json({ answer: answer.trim() });
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function runPythonScript(url) {
  return new Promise((resolve, reject) => {
    let options = {
      mode: 'text',
      pythonOptions: ['-u'], // unbuffered, unbuffered stdout, stderr
      args: [url], // Argument passed to Python script
    };

    PythonShell.run('website_q&a.py', options, function (err, results) {
      if (err) {
        reject(err);
      } else {
        resolve(results);
      }
    });
  });
}

app.post('/runCrawl', async (req, res) => {
  const url = req.body.url; // Get URL from the request body

  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }

  try {
    await runPythonScript(url);
    return res.send('OK');
  } catch (error) {
    console.error(error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
