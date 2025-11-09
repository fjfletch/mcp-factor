/**
 * Next.js API Route Proxy to AWS Backend
 * Solves Mixed Content issue by proxying HTTPS -> HTTP requests server-side
 */

import { NextRequest, NextResponse } from 'next/server';

const AWS_BACKEND_URL = 'http://3.136.147.20:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'POST');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'PATCH');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'DELETE');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params.path, 'PUT');
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string
) {
  // Build target URL
  const path = pathSegments.join('/');
  const searchParams = request.nextUrl.searchParams.toString();
  const targetUrl = `${AWS_BACKEND_URL}/${path}${searchParams ? `?${searchParams}` : ''}`;

  console.log(`[Proxy] ${method} ${targetUrl}`);

  try {
    // Get request body if present
    let body = undefined;
    if (method !== 'GET' && method !== 'DELETE') {
      body = await request.text();
    }

    // Forward the request to AWS backend
    const response = await fetch(targetUrl, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body || undefined,
    });

    // Get response data
    const data = await response.text();
    
    // Return response with CORS headers
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error: any) {
    console.error('[Proxy] Error:', error);
    return NextResponse.json(
      { error: 'Proxy error', details: error.message },
      { status: 500 }
    );
  }
}

// Handle OPTIONS for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
