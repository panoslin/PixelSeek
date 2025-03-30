'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { RadioButton } from 'primereact/radiobutton';
import { Divider } from 'primereact/divider';

export default function PaymentPage() {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState('monthly');

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: '$0',
      period: 'forever',
      features: [
        '10 searches per month',
        'Basic search functionality',
        'Access to public frames',
        'Limited filters',
      ],
      cta: 'Current Plan',
      color: '#666666',
      disabled: true,
    },
    {
      id: 'monthly',
      name: 'Pro Monthly',
      price: '$9.99',
      period: 'per month',
      features: [
        'Unlimited searches',
        'Advanced search filters',
        'Access to all frames',
        'Save collections',
        'Download in HD',
      ],
      cta: 'Choose Plan',
      color: '#daec46',
      popular: true,
    },
    {
      id: 'yearly',
      name: 'Pro Yearly',
      price: '$89.99',
      period: 'per year',
      features: [
        'Everything in Pro Monthly',
        'Save 25% compared to monthly',
        'API access',
        'Priority support',
      ],
      cta: 'Choose Plan',
      color: '#daec46',
      discount: '25% off',
    },
  ];

  const handleChoosePlan = (plan: string) => {
    setSelectedPlan(plan);
  };

  const handleProceedToPayment = () => {
    // Here you would implement payment processing
    console.log(`Processing payment for ${selectedPlan} plan`);
    router.push('/home');
  };

  return (
    <div className="min-h-screen bg-[#121212] py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">Choose Your Plan</h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Upgrade to Pro for unlimited access to all frames and advanced features.
            Cancel anytime, no commitment required.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className={`${
                selectedPlan === plan.id
                  ? 'border-2 border-[#daec46]'
                  : 'border border-[#333333]'
              } bg-[#1a1a1a] shadow-lg`}
            >
              <div className="flex flex-col h-full">
                {plan.popular && (
                  <div className="bg-[#daec46] text-black text-xs font-bold py-1 px-3 rounded-full self-start mb-2">
                    MOST POPULAR
                  </div>
                )}

                {plan.discount && (
                  <div className="bg-[#ff6b6b] text-white text-xs font-bold py-1 px-3 rounded-full self-start mb-2">
                    {plan.discount}
                  </div>
                )}

                <h2 className="text-xl font-bold text-white mb-1">{plan.name}</h2>

                <div className="mb-4">
                  <span className="text-3xl font-bold text-white">{plan.price}</span>
                  <span className="text-gray-400 ml-1">{plan.period}</span>
                </div>

                <Divider />

                <ul className="list-disc pl-5 mb-8 text-gray-300 space-y-2 flex-grow">
                  {plan.features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>

                <div className="mt-auto">
                  <div className="flex items-center mb-3">
                    <RadioButton
                      inputId={plan.id}
                      name="plan"
                      value={plan.id}
                      onChange={() => handleChoosePlan(plan.id)}
                      checked={selectedPlan === plan.id}
                      disabled={plan.disabled}
                    />
                    <label htmlFor={plan.id} className="ml-2 text-white">
                      {selectedPlan === plan.id ? 'Selected' : 'Select'}
                    </label>
                  </div>

                  <Button
                    label={plan.cta}
                    className="w-full"
                    style={{ backgroundColor: plan.color, color: plan.color === '#daec46' ? '#000' : '#fff' }}
                    disabled={plan.disabled || selectedPlan !== plan.id}
                    onClick={handleProceedToPayment}
                  />
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-gray-400 mb-4">
            All plans include a 14-day money-back guarantee. No questions asked.
          </p>
          <Button
            label="Continue with Free Plan"
            className="p-button-link text-[#daec46]"
            onClick={() => router.push('/home')}
          />
        </div>
      </div>
    </div>
  );
}
