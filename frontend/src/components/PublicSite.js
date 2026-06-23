import React, { useState } from 'react';
import { Link } from 'react-router-dom';

// ─── Public Navigation ────────────────────────────────────────────────────────

export const PublicNav = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AS</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Agentic Solutions</span>
          </Link>

          <div className="hidden md:flex items-center space-x-6">
            <Link to="/#products" className="text-gray-600 hover:text-indigo-600 text-sm font-medium transition-colors">Products</Link>
            <Link to="/#pricing" className="text-gray-600 hover:text-indigo-600 text-sm font-medium transition-colors">Pricing</Link>
            <Link to="/contact" className="text-gray-600 hover:text-indigo-600 text-sm font-medium transition-colors">Contact</Link>
            <Link
              to="/dashboard"
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors"
            >
              Launch App
            </Link>
          </div>

          <button
            className="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            onClick={() => setOpen(!open)}
            aria-label="Toggle menu"
          >
            {open ? (
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {open && (
        <div className="md:hidden border-t border-gray-200 bg-white px-4 py-3 space-y-2">
          <Link to="/#products" onClick={() => setOpen(false)} className="block text-gray-600 hover:text-indigo-600 py-2 text-sm font-medium">Products</Link>
          <Link to="/#pricing" onClick={() => setOpen(false)} className="block text-gray-600 hover:text-indigo-600 py-2 text-sm font-medium">Pricing</Link>
          <Link to="/contact" onClick={() => setOpen(false)} className="block text-gray-600 hover:text-indigo-600 py-2 text-sm font-medium">Contact</Link>
          <Link
            to="/dashboard"
            onClick={() => setOpen(false)}
            className="block bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors text-center"
          >
            Launch App
          </Link>
        </div>
      )}
    </nav>
  );
};

// ─── Public Footer ────────────────────────────────────────────────────────────

export const PublicFooter = () => (
  <footer className="bg-gray-900 text-gray-400">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="md:col-span-2">
          <div className="flex items-center space-x-2 mb-3">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AS</span>
            </div>
            <span className="text-white font-bold text-lg">Agentic Solutions</span>
          </div>
          <p className="text-sm leading-relaxed max-w-xs">
            Empowering creators and businesses with autonomous AI agent systems. Build, scale, and automate your content workflows.
          </p>
          <p className="mt-4 text-sm">
            Contact:{' '}
            <a href="mailto:support@agenticsolutions.io" className="text-indigo-400 hover:text-indigo-300">
              support@agenticsolutions.io
            </a>
          </p>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3 text-sm uppercase tracking-wider">Products</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/dashboard" className="hover:text-white transition-colors">Vertano App</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3 text-sm uppercase tracking-wider">Legal</h4>
          <ul className="space-y-2 text-sm">
            <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
            <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
            <li><Link to="/refund-policy" className="hover:text-white transition-colors">Refund Policy</Link></li>
            <li><Link to="/cancellation-policy" className="hover:text-white transition-colors">Cancellation Policy</Link></li>
            <li><Link to="/contact" className="hover:text-white transition-colors">Contact Us</Link></li>
          </ul>
        </div>
      </div>

      <div className="mt-10 pt-6 border-t border-gray-800 flex flex-col sm:flex-row justify-between items-center text-xs gap-3">
        <p>&copy; {new Date().getFullYear()} Agentic Solutions. All rights reserved.</p>
        <p>Agentic Solutions · United States</p>
      </div>
    </div>
  </footer>
);

// ─── Landing Page ─────────────────────────────────────────────────────────────

export const LandingPage = () => (
  <div className="min-h-screen bg-white">
    <PublicNav />

    {/* Hero */}
    <section className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-indigo-800 to-purple-900 text-white">
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-96 h-96 bg-purple-400 rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-400 rounded-full translate-x-1/2 translate-y-1/2 blur-3xl" />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32 text-center">
        <span className="inline-block bg-indigo-700/60 text-indigo-200 text-xs font-semibold px-3 py-1 rounded-full mb-6 uppercase tracking-widest">
          AI-Powered Automation
        </span>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6">
          Build Smarter with<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-purple-300">
            Autonomous AI Agents
          </span>
        </h1>
        <p className="text-lg sm:text-xl text-indigo-200 max-w-2xl mx-auto mb-10">
          Agentic Solutions builds cutting-edge multi-agent AI systems that automate content creation,
          trend discovery, and cross-platform publishing — so you can focus on what matters.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/dashboard"
            className="bg-white text-indigo-900 px-8 py-3 rounded-xl font-bold text-base hover:bg-indigo-50 transition-colors shadow-lg"
          >
            Launch Vertano →
          </Link>
          <a
            href="#products"
            className="border border-white/40 text-white px-8 py-3 rounded-xl font-semibold text-base hover:bg-white/10 transition-colors"
          >
            Learn More
          </a>
        </div>
      </div>
    </section>

    {/* Features */}
    <section className="bg-gray-50 py-16 lg:py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Why Agentic Solutions?</h2>
          <p className="text-gray-500 max-w-xl mx-auto">We combine specialized AI agents into seamless workflows that run 24/7 on your behalf.</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: '🤖',
              title: 'Multi-Agent AI',
              desc: 'Seven+ specialized AI agents collaborate to research, write, and publish content autonomously.',
            },
            {
              icon: '📈',
              title: 'Trend Discovery',
              desc: 'Automatically surface what is trending across the web and social platforms every week.',
            },
            {
              icon: '🎙️',
              title: 'Voice Cloning',
              desc: 'Clone your voice and narrate AI-written content with studio-quality audio output.',
            },
            {
              icon: '🎨',
              title: 'Branding Kit',
              desc: 'Generate on-brand visuals, copy styles, and tone-consistent content at scale.',
            },
            {
              icon: '🌐',
              title: 'Multi-Platform',
              desc: 'Publish across LinkedIn, Instagram, newsletters, and more from a single dashboard.',
            },
            {
              icon: '⚡',
              title: 'Fusion Studio',
              desc: 'Blend your own prompts with our autonomous pipeline for a truly hybrid workflow.',
            },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Products */}
    <section id="products" className="py-16 lg:py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Our Products</h2>
          <p className="text-gray-500 max-w-xl mx-auto">Everything Agentic Solutions offers under one roof.</p>
        </div>
        <div className="max-w-2xl mx-auto">
          <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl p-8 text-white shadow-2xl">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <span className="text-2xl font-bold">V</span>
              </div>
              <div>
                <h3 className="text-2xl font-extrabold">Vertano</h3>
                <p className="text-indigo-200 text-sm">by Agentic Solutions</p>
              </div>
            </div>
            <p className="text-indigo-100 mb-6 leading-relaxed">
              Vertano is an emergent AI multi-agent content creation system. It discovers trending topics,
              generates multi-platform content, clones your voice, and maintains your brand identity —
              all on autopilot.
            </p>
            <ul className="space-y-2 mb-8">
              {[
                'Autonomous trend research & topic discovery',
                'AI-written long-form and short-form content',
                'Voice cloning & audio narration',
                'Branding kit & visual identity generation',
                'Multi-platform scheduling and publishing',
                'Fusion Studio for custom workflow integration',
              ].map((item) => (
                <li key={item} className="flex items-start text-sm text-indigo-100">
                  <span className="mr-2 mt-0.5 text-green-300">✓</span>
                  {item}
                </li>
              ))}
            </ul>
            <Link
              to="/dashboard"
              className="inline-block bg-white text-indigo-700 font-bold px-6 py-3 rounded-xl hover:bg-indigo-50 transition-colors"
            >
              Open Vertano →
            </Link>
          </div>
        </div>
      </div>
    </section>

    {/* Pricing */}
    <section id="pricing" className="bg-gray-50 py-16 lg:py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Simple, Transparent Pricing</h2>
          <p className="text-gray-500 max-w-xl mx-auto">All plans include access to Vertano. Cancel any time.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            {
              name: 'Starter',
              price: '$29',
              period: '/month',
              desc: 'Perfect for solo creators.',
              features: ['Up to 20 content pieces/month', 'Trend discovery', '3 platforms', 'Email support'],
              cta: 'Get Started',
              highlight: false,
            },
            {
              name: 'Professional',
              price: '$79',
              period: '/month',
              desc: 'For growing teams and brands.',
              features: [
                'Unlimited content pieces',
                'Trend discovery & analytics',
                'All platforms',
                'Voice cloning',
                'Branding kit',
                'Priority support',
              ],
              cta: 'Start Free Trial',
              highlight: true,
            },
            {
              name: 'Enterprise',
              price: '$199',
              period: '/month',
              desc: 'For agencies and large teams.',
              features: [
                'Everything in Professional',
                'Up to 10 team members',
                'Custom agent workflows',
                'Fusion Studio',
                'Dedicated account manager',
                'SLA guarantee',
              ],
              cta: 'Contact Us',
              highlight: false,
            },
          ].map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-8 border ${
                plan.highlight
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-2xl scale-105'
                  : 'bg-white text-gray-900 border-gray-200 shadow-sm'
              }`}
            >
              <h3 className={`text-lg font-bold mb-1 ${plan.highlight ? 'text-white' : 'text-gray-900'}`}>{plan.name}</h3>
              <p className={`text-sm mb-4 ${plan.highlight ? 'text-indigo-200' : 'text-gray-500'}`}>{plan.desc}</p>
              <div className="flex items-end mb-6">
                <span className={`text-4xl font-extrabold ${plan.highlight ? 'text-white' : 'text-gray-900'}`}>{plan.price}</span>
                <span className={`text-sm ml-1 mb-1 ${plan.highlight ? 'text-indigo-200' : 'text-gray-500'}`}>{plan.period}</span>
              </div>
              <ul className="space-y-2 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className={`flex items-start text-sm ${plan.highlight ? 'text-indigo-100' : 'text-gray-600'}`}>
                    <span className={`mr-2 mt-0.5 ${plan.highlight ? 'text-green-300' : 'text-green-500'}`}>✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                to={plan.name === 'Enterprise' ? '/contact' : '/dashboard'}
                className={`block text-center font-semibold py-3 rounded-xl transition-colors ${
                  plan.highlight
                    ? 'bg-white text-indigo-700 hover:bg-indigo-50'
                    : 'bg-indigo-600 text-white hover:bg-indigo-700'
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
        <p className="text-center text-gray-500 text-sm mt-8">
          Prices are in USD. All subscriptions are billed monthly. Cancel any time with no penalties.
        </p>
      </div>
    </section>

    {/* Contact CTA */}
    <section className="py-16 lg:py-20">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to automate your content?</h2>
        <p className="text-gray-500 mb-8">
          Have questions before signing up? Our team is happy to help.
        </p>
        <Link
          to="/contact"
          className="inline-block bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700 transition-colors"
        >
          Get in Touch
        </Link>
      </div>
    </section>

    <PublicFooter />
  </div>
);

// ─── Contact Page ─────────────────────────────────────────────────────────────

export const ContactPage = () => (
  <div className="min-h-screen bg-white flex flex-col">
    <PublicNav />
    <div className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-4">Contact Us</h1>
      <p className="text-gray-500 mb-10 text-lg">
        We're here to help. Reach out and we'll respond as quickly as possible.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Agentic Solutions</h2>
            <p className="text-gray-500 text-sm">Business address: United States</p>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Customer Support</h3>
            <p className="text-gray-600 text-sm">For billing, account issues, refunds, and general questions:</p>
            <a
              href="mailto:support@agenticsolutions.io"
              className="text-indigo-600 font-semibold hover:underline"
            >
              support@agenticsolutions.io
            </a>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Sales &amp; Partnerships</h3>
            <p className="text-gray-600 text-sm">For enterprise plans and partnerships:</p>
            <a
              href="mailto:hello@agenticsolutions.io"
              className="text-indigo-600 font-semibold hover:underline"
            >
              hello@agenticsolutions.io
            </a>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Response Times</h3>
            <p className="text-gray-600 text-sm">
              We aim to respond to all inquiries within <strong>1 business day</strong>.
              Enterprise customers receive priority support with a guaranteed response within 4 hours.
            </p>
          </div>

          <div className="bg-indigo-50 rounded-xl p-4 text-sm text-indigo-800">
            <p className="font-semibold mb-1">Refund or Dispute?</p>
            <p>Email <a href="mailto:support@agenticsolutions.io" className="underline">support@agenticsolutions.io</a> with your account email and a description of the issue. See our <Link to="/refund-policy" className="underline">Refund Policy</Link> for details.</p>
          </div>
        </div>

        <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200">
          <h3 className="font-bold text-gray-900 mb-4">Quick Message</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              alert('Message sent! We\'ll be in touch within 1 business day.');
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
              <input
                type="text"
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Jane Smith"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <input
                type="email"
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="jane@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                required
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                placeholder="How can we help you?"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Send Message
            </button>
          </form>
        </div>
      </div>
    </div>
    <PublicFooter />
  </div>
);

// ─── Terms of Service ─────────────────────────────────────────────────────────

export const TermsPage = () => (
  <div className="min-h-screen bg-white flex flex-col">
    <PublicNav />
    <div className="flex-1 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2">Terms of Service</h1>
      <p className="text-gray-400 text-sm mb-10">Last updated: June 23, 2026</p>

      <div className="prose prose-gray max-w-none space-y-8 text-gray-700 text-sm leading-relaxed">

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">1. Agreement to Terms</h2>
          <p>
            By accessing or using any product or service offered by <strong>Agentic Solutions</strong>
            ("Company," "we," "us," or "our"), including the Vertano platform, you agree to be bound by
            these Terms of Service ("Terms"). If you do not agree, do not use our services.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">2. Description of Services</h2>
          <p>
            Agentic Solutions provides AI-powered content automation software. Our primary product,
            <strong> Vertano</strong>, is a subscription-based Software-as-a-Service (SaaS) platform
            that uses multi-agent AI systems to discover trending topics, generate multi-platform content,
            clone user voices, and automate publishing workflows.
          </p>
          <p className="mt-2">
            All services are digital and delivered electronically. We do not sell physical goods.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">3. Subscriptions and Billing</h2>
          <p>
            Vertano is offered on a recurring monthly subscription basis. By subscribing, you authorize
            Agentic Solutions to charge your payment method on a monthly cycle. Prices are listed in
            USD and are exclusive of any applicable taxes.
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>Starter Plan: $29/month</li>
            <li>Professional Plan: $79/month</li>
            <li>Enterprise Plan: $199/month</li>
          </ul>
          <p className="mt-2">
            Subscription fees are non-refundable except as described in our{' '}
            <Link to="/refund-policy" className="text-indigo-600 underline">Refund Policy</Link>.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">4. Acceptable Use</h2>
          <p>You agree not to use our services to:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>Generate or distribute illegal, defamatory, or harmful content</li>
            <li>Infringe the intellectual property rights of others</li>
            <li>Attempt to reverse-engineer, scrape, or damage our platform</li>
            <li>Circumvent any access controls or security measures</li>
            <li>Violate any applicable local, national, or international laws</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">5. Intellectual Property</h2>
          <p>
            All content, code, trademarks, and materials on our platform are the property of Agentic
            Solutions or our licensors. You retain ownership of content you create using our tools,
            subject to the licenses granted in these Terms.
          </p>
          <p className="mt-2">
            You grant Agentic Solutions a limited, non-exclusive license to process your inputs and
            outputs solely to provide the service.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">6. Promotions</h2>
          <p>
            From time to time, Agentic Solutions may offer promotional pricing, free trials, or discount
            codes. Unless otherwise stated:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>Promotions apply to new subscribers only unless explicitly stated otherwise</li>
            <li>Promotional pricing applies only for the stated promotional period; standard rates apply thereafter</li>
            <li>Promotional codes are single-use and non-transferable</li>
            <li>Free trials automatically convert to paid subscriptions at the end of the trial period unless cancelled beforehand</li>
            <li>Agentic Solutions reserves the right to modify or discontinue promotions at any time</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">7. Disclaimer of Warranties</h2>
          <p>
            Our services are provided "as is" without any warranty of any kind, express or implied.
            We do not warrant that the service will be uninterrupted, error-free, or that AI-generated
            content will be accurate or suitable for any particular purpose.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">8. Limitation of Liability</h2>
          <p>
            To the fullest extent permitted by law, Agentic Solutions shall not be liable for any
            indirect, incidental, special, or consequential damages. Our total liability shall not
            exceed the amount paid by you in the three months preceding the claim.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">9. Legal and Export Restrictions</h2>
          <p>
            Our services are operated from the United States. You are responsible for compliance with
            all local laws applicable to your use. You agree not to export or re-export our services or
            technology in violation of U.S. export laws, including the Export Administration Regulations
            (EAR) and sanctions administered by the Office of Foreign Assets Control (OFAC). Our
            services are not available to persons in countries subject to U.S. trade sanctions.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">10. Changes to Terms</h2>
          <p>
            We may update these Terms at any time. We will notify you by email or via the platform.
            Continued use of our services after changes constitutes acceptance of the revised Terms.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">11. Contact</h2>
          <p>
            For questions about these Terms, contact us at{' '}
            <a href="mailto:support@agenticsolutions.io" className="text-indigo-600 underline">
              support@agenticsolutions.io
            </a>.
          </p>
        </section>
      </div>
    </div>
    <PublicFooter />
  </div>
);

// ─── Privacy Policy ───────────────────────────────────────────────────────────

export const PrivacyPage = () => (
  <div className="min-h-screen bg-white flex flex-col">
    <PublicNav />
    <div className="flex-1 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2">Privacy Policy</h1>
      <p className="text-gray-400 text-sm mb-10">Last updated: June 23, 2026</p>

      <div className="prose prose-gray max-w-none space-y-8 text-gray-700 text-sm leading-relaxed">
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">1. Information We Collect</h2>
          <p>We collect the following types of information:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li><strong>Account information:</strong> name, email address, password</li>
            <li><strong>Billing information:</strong> processed securely through Stripe; we do not store card numbers</li>
            <li><strong>Usage data:</strong> feature usage, session data, browser type, IP address</li>
            <li><strong>Content you create:</strong> prompts, generated content, uploaded voice samples</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">2. How We Use Your Information</h2>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>To provide and improve our services</li>
            <li>To process payments and manage subscriptions</li>
            <li>To send transactional emails (receipts, password resets)</li>
            <li>To comply with legal obligations</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">3. Sharing of Information</h2>
          <p>
            We do not sell your personal data. We share data with trusted service providers (e.g., Stripe for
            payments, cloud hosting providers) only as necessary to operate our services, and they are bound
            by confidentiality obligations.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">4. Data Retention</h2>
          <p>
            We retain your data for as long as your account is active or as needed to provide services.
            After account deletion, data is purged within 30 days, except where retention is required by law.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">5. Your Rights</h2>
          <p>
            You may request access to, correction of, or deletion of your personal data by contacting{' '}
            <a href="mailto:support@agenticsolutions.io" className="text-indigo-600 underline">
              support@agenticsolutions.io
            </a>.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">6. Cookies</h2>
          <p>
            We use essential cookies to operate our platform and analytics cookies to understand usage.
            You may disable non-essential cookies in your browser settings.
          </p>
        </section>
      </div>
    </div>
    <PublicFooter />
  </div>
);

// ─── Refund & Dispute Policy ──────────────────────────────────────────────────

export const RefundPolicyPage = () => (
  <div className="min-h-screen bg-white flex flex-col">
    <PublicNav />
    <div className="flex-1 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2">Refund &amp; Dispute Policy</h1>
      <p className="text-gray-400 text-sm mb-10">Last updated: June 23, 2026</p>

      <div className="prose prose-gray max-w-none space-y-8 text-gray-700 text-sm leading-relaxed">

        <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-indigo-800">
          <p className="font-semibold">No Physical Goods</p>
          <p className="mt-1">
            Agentic Solutions sells digital subscription services only. We do not sell or ship physical
            goods, so there is no physical return process.
          </p>
        </div>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Refund Eligibility</h2>
          <p>We offer refunds in the following situations:</p>
          <ul className="list-disc pl-5 mt-2 space-y-2">
            <li>
              <strong>Within 7 days of first payment:</strong> If you are unsatisfied with Vertano
              after subscribing for the first time, you may request a full refund within 7 calendar
              days of your initial charge.
            </li>
            <li>
              <strong>Service outage:</strong> If our service was unavailable for more than 24
              consecutive hours in a billing period due to issues on our end, you may request a
              pro-rated credit or refund.
            </li>
            <li>
              <strong>Duplicate charge:</strong> If you were charged more than once for the same
              billing period, we will refund the duplicate charge in full.
            </li>
            <li>
              <strong>Unauthorized charge:</strong> If you believe a charge was made without your
              authorization, contact us immediately.
            </li>
          </ul>
          <p className="mt-3">
            Renewal charges after the first billing period are generally non-refundable. We encourage
            you to cancel before your renewal date if you no longer wish to use the service.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">How to Request a Refund</h2>
          <ol className="list-decimal pl-5 mt-2 space-y-2">
            <li>Email <a href="mailto:support@agenticsolutions.io" className="text-indigo-600 underline">support@agenticsolutions.io</a> with the subject line: <strong>Refund Request</strong></li>
            <li>Include your account email address and the reason for your request</li>
            <li>Our team will respond within 2 business days</li>
            <li>Approved refunds are processed within 5–10 business days and returned to your original payment method</li>
          </ol>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Dispute Resolution</h2>
          <p>
            If you have a billing dispute, please contact us first at{' '}
            <a href="mailto:support@agenticsolutions.io" className="text-indigo-600 underline">
              support@agenticsolutions.io
            </a>{' '}
            before initiating a chargeback with your bank or card provider. We are committed to
            resolving disputes fairly and promptly.
          </p>
          <p className="mt-2">
            If we cannot resolve your dispute directly, you may escalate via your card issuer or
            payment processor. We will cooperate with all legitimate chargeback investigations.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Exceptions</h2>
          <p>Refunds will not be issued for:</p>
          <ul className="list-disc pl-5 mt-2 space-y-1">
            <li>Charges older than 30 days (unless due to unauthorized use)</li>
            <li>Accounts terminated for violating our Terms of Service</li>
            <li>Promotional or discounted subscription periods (unless required by law)</li>
          </ul>
        </section>
      </div>
    </div>
    <PublicFooter />
  </div>
);

// ─── Cancellation Policy ──────────────────────────────────────────────────────

export const CancellationPolicyPage = () => (
  <div className="min-h-screen bg-white flex flex-col">
    <PublicNav />
    <div className="flex-1 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-2">Cancellation Policy</h1>
      <p className="text-gray-400 text-sm mb-10">Last updated: June 23, 2026</p>

      <div className="prose prose-gray max-w-none space-y-8 text-gray-700 text-sm leading-relaxed">

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Cancel Any Time</h2>
          <p>
            You may cancel your Vertano subscription at any time with no penalties or cancellation fees.
            Your subscription will remain active until the end of the current billing period, after which
            it will not renew.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">How to Cancel</h2>
          <p>You can cancel your subscription in two ways:</p>
          <ol className="list-decimal pl-5 mt-2 space-y-2">
            <li>
              <strong>Via account settings:</strong> Log in to Vertano, navigate to your Account
              Settings, and select "Cancel Subscription."
            </li>
            <li>
              <strong>Via email:</strong> Send a cancellation request to{' '}
              <a href="mailto:support@agenticsolutions.io" className="text-indigo-600 underline">
                support@agenticsolutions.io
              </a>{' '}
              with your account email. We will process the cancellation within 1 business day and
              send you a confirmation.
            </li>
          </ol>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">What Happens After Cancellation</h2>
          <ul className="list-disc pl-5 mt-2 space-y-2">
            <li>You retain full access to Vertano until the end of your paid billing period</li>
            <li>No further charges will be made after cancellation</li>
            <li>Your data is retained for 30 days after cancellation, after which it is permanently deleted</li>
            <li>You may re-subscribe at any time; data from previous sessions may not be recoverable after deletion</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Timing</h2>
          <p>
            To avoid being charged for the next billing cycle, cancel <strong>before</strong> your
            renewal date. The exact renewal date is shown in your account settings. Cancellations
            submitted after the renewal date apply to the following billing period.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Pausing Your Subscription</h2>
          <p>
            If you need a break but don't want to lose your data and settings, contact us at{' '}
            <a href="mailto:support@agenticsolutions.io" className="text-indigo-600 underline">
              support@agenticsolutions.io
            </a>. We offer subscription pauses of up to 3 months for qualifying accounts.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Contact</h2>
          <p>
            Questions about cancellation? Email{' '}
            <a href="mailto:support@agenticsolutions.io" className="text-indigo-600 underline">
              support@agenticsolutions.io
            </a>{' '}
            — we're happy to help.
          </p>
        </section>
      </div>
    </div>
    <PublicFooter />
  </div>
);
