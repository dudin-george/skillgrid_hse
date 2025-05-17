import React from 'react';

const About: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">About SkillGrid</h1>
      
      <div className="prose prose-lg max-w-none">
        <p className="text-xl text-gray-600 mb-6">
          SkillGrid is an AI-powered platform designed to connect IT specialists with the perfect job opportunities based on comprehensive skill assessments.
        </p>
        
        <h2 className="text-2xl font-bold text-gray-900 mt-10 mb-4">Our Mission</h2>
        <p className="text-lg text-gray-600 mb-6">
          Our mission is to transform the way IT professionals find jobs by creating a transparent, skills-based matching system that benefits both job seekers and employers.
        </p>
        
        <h2 className="text-2xl font-bold text-gray-900 mt-10 mb-4">Our Vision</h2>
        <p className="text-lg text-gray-600 mb-6">
          We envision a world where every IT professional finds fulfilling work that aligns with their skills and aspirations, and every company finds the perfect talent to drive innovation and growth.
        </p>
        
        <h2 className="text-2xl font-bold text-gray-900 mt-10 mb-4">Our Team</h2>
        <p className="text-lg text-gray-600 mb-6">
          SkillGrid was founded by a team of IT professionals and HR experts who experienced firsthand the challenges of the traditional recruitment process. We combined our expertise in technology, recruitment, and AI to create a platform that addresses these challenges.
        </p>
      </div>
    </div>
  );
};

export default About; 