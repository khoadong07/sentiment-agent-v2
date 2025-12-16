#!/usr/bin/env python3
"""
Load testing script cho Sentiment Analysis API
"""
import asyncio
import aiohttp
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
import argparse

# Test data samples
TEST_SAMPLES = [
    {
        "id": "test_1",
        "index": "6641ccbdf4901a7ae602197f",
        "title": "Máy lọc không khí Dyson rất tốt, đáng đồng tiền bát gạo",
        "content": "Mình vừa mua máy lọc Dyson về dùng thử, cảm giác rất hài lòng",
        "description": "Review máy lọc không khí dyson v15 detect",
        "type": "fbGroupTopic"
    },
    {
        "id": "test_2", 
        "index": "6641ccbdf4901a7ae602197f",
        "title": "Máy lọc Sharp bị hỏng sau 1 tháng sử dụng",
        "content": "Chất lượng kém, không đáng tiền",
        "description": "Máy lọc không khí sharp bị lỗi",
        "type": "fbGroupTopic"
    },
    {
        "id": "test_3",
        "index": "6641ccbdf4901a7ae602197f", 
        "title": "Hôm nay trời đẹp quá",
        "content": "Đi chơi công viên với gia đình",
        "description": "Cuối tuần vui vẻ",
        "type": "fbGroupTopic"
    }
]

class LoadTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    async def single_request(self, session, data):
        """Thực hiện một request và đo thời gian"""
        start_time = time.time()
        
        try:
            async with session.post(
                f"{self.base_url}/analyze",
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response_time": response_time,
                        "status": response.status,
                        "sentiment": result.get("sentiment"),
                        "targeted": result.get("targeted")
                    }
                else:
                    return {
                        "success": False,
                        "response_time": response_time,
                        "status": response.status,
                        "error": await response.text()
                    }
                    
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": end_time - start_time,
                "status": 0,
                "error": str(e)
            }
    
    async def concurrent_test(self, concurrent_users=10, requests_per_user=10):
        """Test với nhiều user đồng thời"""
        print(f"🚀 Starting load test: {concurrent_users} concurrent users, {requests_per_user} requests each")
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            for user_id in range(concurrent_users):
                for req_id in range(requests_per_user):
                    # Rotate through test samples
                    sample = TEST_SAMPLES[req_id % len(TEST_SAMPLES)].copy()
                    sample["id"] = f"user_{user_id}_req_{req_id}"
                    
                    task = self.single_request(session, sample)
                    tasks.append(task)
            
            # Execute all requests concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Process results
            successful_requests = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_requests = [r for r in results if isinstance(r, dict) and not r.get("success")]
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            self.print_results(
                successful_requests, 
                failed_requests, 
                exceptions, 
                total_time,
                concurrent_users,
                requests_per_user
            )
    
    def print_results(self, successful, failed, exceptions, total_time, users, requests_per_user):
        """In kết quả load test"""
        total_requests = len(successful) + len(failed) + len(exceptions)
        success_rate = len(successful) / total_requests * 100 if total_requests > 0 else 0
        
        print(f"\n📊 Load Test Results")
        print(f"{'='*50}")
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {len(successful)} ({success_rate:.1f}%)")
        print(f"Failed: {len(failed)}")
        print(f"Exceptions: {len(exceptions)}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests/Second: {total_requests/total_time:.2f}")
        
        if successful:
            response_times = [r["response_time"] for r in successful]
            print(f"\n⏱️  Response Time Statistics:")
            print(f"Average: {statistics.mean(response_times):.3f}s")
            print(f"Median: {statistics.median(response_times):.3f}s")
            print(f"Min: {min(response_times):.3f}s")
            print(f"Max: {max(response_times):.3f}s")
            print(f"95th percentile: {statistics.quantiles(response_times, n=20)[18]:.3f}s")
            
            # Sentiment distribution
            sentiments = {}
            for r in successful:
                sentiment = r.get("sentiment", "unknown")
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
            
            print(f"\n🎯 Sentiment Distribution:")
            for sentiment, count in sentiments.items():
                print(f"{sentiment}: {count}")
        
        if failed:
            print(f"\n❌ Failed Requests:")
            status_codes = {}
            for r in failed:
                status = r.get("status", "unknown")
                status_codes[status] = status_codes.get(status, 0) + 1
            
            for status, count in status_codes.items():
                print(f"Status {status}: {count}")
        
        if exceptions:
            print(f"\n💥 Exceptions:")
            for i, exc in enumerate(exceptions[:5]):  # Show first 5 exceptions
                print(f"{i+1}. {type(exc).__name__}: {str(exc)}")

    async def health_check(self):
        """Kiểm tra health của API trước khi test"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ API Health Check: {data.get('status')}")
                        return True
                    else:
                        print(f"❌ API Health Check Failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ API Health Check Error: {str(e)}")
            return False

async def main():
    parser = argparse.ArgumentParser(description="Load test Sentiment Analysis API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--users", type=int, default=10, help="Concurrent users")
    parser.add_argument("--requests", type=int, default=10, help="Requests per user")
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url)
    
    # Health check first
    if not await tester.health_check():
        print("❌ API is not healthy. Aborting load test.")
        return
    
    # Run load test
    await tester.concurrent_test(args.users, args.requests)

if __name__ == "__main__":
    asyncio.run(main())