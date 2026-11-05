// Stands in for the claude.ai artifact database: the daily log calls
// window.claude.use('db') and gets this, backed by the local server.
(function(){
  function db(){
    return {
      doc: function(path){
        var day = path.split('/')[1];
        return { set: function(body){
          return fetch('/api/days/' + day, {method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
            .then(function(r){ if(!r.ok) throw new Error('server said ' + r.status); });
        }};
      },
      collection: function(){
        return { onSnapshot: function(ok, fail){
          fetch('/api/days').then(function(r){ if(!r.ok) throw new Error('server said ' + r.status); return r.json(); })
            .then(function(days){
              ok({docs: Object.keys(days).map(function(k){ return {id:k, data:function(){ return days[k]; }}; })});
            }).catch(function(e){ fail && fail(e); });
        }};
      }
    };
  }
  window.claude = { use: function(){ return Promise.resolve(db()); } };
})();
