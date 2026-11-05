const {defineConfig}=require('@playwright/test');
const managedServer=process.env.NUMLEARN_TEST_SERVER==='1';
const managedURL='http://127.0.0.1:8767';
module.exports=defineConfig({
  testDir:'tests/browser', timeout:45000, workers:1,
  use:{baseURL:managedServer?managedURL:process.env.NUMLEARN_TEST_URL||'http://127.0.0.1:8765',channel:'chrome',viewport:{width:1440,height:1000},screenshot:'only-on-failure',trace:'retain-on-failure'},
  webServer:managedServer?{
    command:'NUMLEARN_DEBUG=True ALLOW_SQLITE=True SECRET_KEY=local-validation-only DATABASE_URL= .venv/bin/python manage.py runserver 127.0.0.1:8767 --noreload',
    url:managedURL,reuseExistingServer:false,timeout:30000,stdout:'ignore',stderr:'ignore',
  }:undefined,
  reporter:'list'
});
