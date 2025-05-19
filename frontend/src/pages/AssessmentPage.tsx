import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOry } from '../context/OryContext';

// Sample task data
const sampleTask = {
  title: "Python Function Challenge",
  description: `Write a function called 'calculate_factorial' that takes an integer 'n' as input and returns the factorial of that number.

The factorial of a non-negative integer n is the product of all positive integers less than or equal to n.

Example:
- factorial(5) should return 120 (because 5 * 4 * 3 * 2 * 1 = 120)
- factorial(0) should return 1 (by definition)

Your function should handle the edge case of n = 0 correctly.`,
  initialCode: `def calculate_factorial(n):
    # Your code here
    pass

# Test cases
print(calculate_factorial(5))  # Should output: 120
print(calculate_factorial(0))  # Should output: 1
`,
  timeLimit: 30 * 60 // 30 minutes in seconds
};

const AssessmentPage: React.FC = () => {
  const { isLoading } = useOry();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [task, setTask] = useState(sampleTask);
  const [code, setCode] = useState('');
  const [result, setResult] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(task.timeLimit);

  // Format time as HH:MM:SS
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return [
      hours.toString().padStart(2, '0'),
      minutes.toString().padStart(2, '0'),
      secs.toString().padStart(2, '0')
    ].join(':');
  };

  // In a real application, you would fetch task details from an API
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check authentication status with backend
        const response = await fetch('https://api.skillgrid.tech/auth', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        // If not authenticated, redirect to home
        if (!response.ok) {
          navigate('/');
          return;
        }
        
        // In a real app, you would fetch task details here
        // For now, we just simulate a network request
        setTimeout(() => {
          setCode(sampleTask.initialCode);
          setLoading(false);
        }, 500);
        
      } catch (error) {
        console.error('Authentication check failed:', error);
        navigate('/');
      }
    };
    
    if (!isLoading) {
      checkAuth();
    }
  }, [isLoading, navigate]);

  // Timer effect
  useEffect(() => {
    if (loading) return;
    
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          // In a real app, auto-submit when time is up
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [loading]);

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCode(e.target.value);
  };

  const handleCompile = () => {
    // In a real app, this would send the code to a backend service
    // For demo purposes, we'll just simulate execution
    try {
      setResult("Compiling...");
      
      // Simulate compilation delay
      setTimeout(() => {
        // Simple pattern match to simulate evaluation
        if (code.includes('def calculate_factorial') && 
            code.includes('return') && 
            !code.includes('pass')) {
          setResult("Output:\n120\n1\n\nExecution successful.");
        } else {
          setResult("Error: Your function is incomplete or incorrect. Please check your implementation.");
        }
      }, 1000);
    } catch (error) {
      setResult(`Error: ${error}`);
    }
  };

  const handleNext = () => {
    // Navigate to results page after completing the assessment
    navigate('/assessment-results');
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Time Remaining */}
      <div className="py-4 text-center border-b border-gray-200">
        <p className="text-lg font-medium text-gray-700">Time Remaining: {formatTime(timeRemaining)}</p>
        <div className="max-w-3xl mx-auto mt-2 bg-gray-200 rounded-full h-1.5 overflow-hidden">
          <div 
            className="bg-blue-600 h-1.5 rounded-full transition-all duration-1000" 
            style={{ width: `${(timeRemaining / task.timeLimit) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Task Panel */}
          <div className="flex flex-col">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Task</h2>
            <div className="bg-gray-50 rounded-lg border border-gray-200 shadow-sm p-4 flex-grow overflow-auto">
              <h3 className="text-lg font-semibold mb-2">{task.title}</h3>
              <div className="text-gray-700 whitespace-pre-line">
                {task.description}
              </div>
            </div>
          </div>

          {/* Code Editor Panel */}
          <div className="flex flex-col">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Code</h2>
            <div className="flex-grow flex flex-col">
              <textarea
                className="w-full flex-grow bg-gray-50 font-mono text-gray-800 p-4 border border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={code}
                onChange={handleCodeChange}
                spellCheck="false"
                autoComplete="off"
              />
            </div>
          </div>
        </div>

        {/* Result Panel */}
        <div className="mt-6">
          <h2 className="text-xl font-bold text-gray-900 mb-3">Result</h2>
          <div className="bg-gray-50 border border-gray-200 rounded-lg shadow-sm p-4 h-32 overflow-auto font-mono whitespace-pre-line">
            {result}
          </div>
        </div>

        {/* Control Buttons */}
        <div className="mt-6 flex justify-end space-x-4">
          <button
            onClick={handleCompile}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition"
          >
            Compile
          </button>
          <button
            onClick={handleNext}
            className="px-6 py-2 bg-blue-600 border border-transparent rounded-md text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssessmentPage; 