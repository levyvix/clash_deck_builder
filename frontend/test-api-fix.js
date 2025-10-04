// Quick test to verify the API fix
const API_BASE_URL = 'http://localhost:8000';

async function testCardsAPI() {
    console.log('🧪 Testing Cards API Fix...');
    console.log('📍 API Base URL:', API_BASE_URL);

    try {
        const url = `${API_BASE_URL}/api/cards/cards`;
        console.log('🔗 Testing URL:', url);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        console.log('📊 Response Status:', response.status, response.statusText);

        if (response.ok) {
            const data = await response.json();
            console.log('✅ SUCCESS! Cards API is working');
            console.log('📦 Received', data.length, 'cards');
            console.log('🃏 First card:', data[0]?.name || 'No cards found');
            console.log('🎯 API Fix Status: WORKING ✅');
        } else {
            console.log('❌ FAILED! Response not OK');
            console.log('🎯 API Fix Status: FAILED ❌');
        }
    } catch (error) {
        console.log('❌ ERROR:', error.message);
        console.log('🎯 API Fix Status: ERROR ❌');
    }
}

// Test the old endpoint to confirm it fails
async function testOldEndpoint() {
    console.log('\n🧪 Testing Old Endpoint (should fail)...');

    try {
        const url = `${API_BASE_URL}/cards/cards`;
        console.log('🔗 Testing URL:', url);

        const response = await fetch(url);
        console.log('📊 Response Status:', response.status, response.statusText);

        if (response.status === 404) {
            console.log('✅ EXPECTED! Old endpoint correctly returns 404');
        } else {
            console.log('⚠️  UNEXPECTED! Old endpoint should return 404');
        }
    } catch (error) {
        console.log('❌ ERROR:', error.message);
    }
}

// Run tests
testCardsAPI().then(() => testOldEndpoint());