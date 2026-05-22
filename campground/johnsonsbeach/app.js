// Johnsons Beach Campground — shared interactions
(function(){
    var nav=document.getElementById('nav');
    if(nav)window.addEventListener('scroll',function(){nav.classList.toggle('scrolled',window.scrollY>40)},{passive:true});
    var t=document.getElementById('navToggle'),l=document.getElementById('navLinks');
    if(t&&l){
        t.addEventListener('click',function(){t.classList.toggle('open');l.classList.toggle('open')});
        l.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){t.classList.remove('open');l.classList.remove('open')})});
    }
    (function(){
        var imgExt=/\.(jpe?g|png|webp|gif|avif)(\?.*)?$/i;
        var triggers=Array.prototype.filter.call(document.querySelectorAll('a[href]'),function(a){var href=a.getAttribute('href')||'';return imgExt.test(href)&&!a.hasAttribute('data-no-lightbox');});
        if(!triggers.length)return;
        var box=document.createElement('div');box.className='lightbox';box.setAttribute('aria-hidden','true');
        box.innerHTML='<button class="lightbox-close" type="button" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="22" height="22"><path d="M6 6l12 12M18 6L6 18"/></svg></button><figure class="lightbox-figure"><img alt="" /><figcaption class="lightbox-cap"></figcaption></figure>';
        document.body.appendChild(box);
        var imgEl=box.querySelector('img'),capEl=box.querySelector('.lightbox-cap'),closeBtn=box.querySelector('.lightbox-close'),lastFocus=null;
        function captionFor(a){var cap=a.querySelector('.cap');if(cap)return cap.textContent.trim();var img=a.querySelector('img');return img&&img.alt?img.alt:''}
        function open(href,alt,caption,trigger){lastFocus=trigger||document.activeElement;imgEl.src=href;imgEl.alt=alt||'';if(caption){capEl.textContent=caption}else{capEl.textContent=''}box.classList.add('open');box.setAttribute('aria-hidden','false');document.documentElement.style.overflow='hidden';setTimeout(function(){closeBtn.focus()},50)}
        function close(){box.classList.remove('open');box.setAttribute('aria-hidden','true');document.documentElement.style.overflow='';imgEl.src='';if(lastFocus&&typeof lastFocus.focus==='function')lastFocus.focus()}
        triggers.forEach(function(a){a.removeAttribute('target');a.addEventListener('click',function(e){if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button===1)return;e.preventDefault();var inner=a.querySelector('img');open(a.getAttribute('href'),inner?inner.alt:'',captionFor(a),a)})});
        box.addEventListener('click',function(e){if(e.target===box||e.target.closest('.lightbox-close'))close()});
        document.addEventListener('keydown',function(e){if(e.key==='Escape'&&box.classList.contains('open'))close()});
    })();
    if('IntersectionObserver' in window){
        var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.14,rootMargin:'0px 0px -40px 0px'});
        document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
    }else document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in')});
})();
