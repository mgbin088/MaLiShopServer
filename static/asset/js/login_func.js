// JavaScript Document
var submit_disabled = true;
var isTrue=0;//验证码 reg
var isTrue2=0;//验证码 找回密码
var isTrue3=0;//邮箱验证码 reg


//登出
function dologout(){
	$.ajax({
			url:"index" ,
			data:{'module':'login','name':'dologout'},
			type:"GET",
			success:function(data){
				window.location = window.location;
			}
	 });	
}

//登陆
function login(){
	var username = $("input[name=login_username]").val();
	var password = $("input[name=login_password]").val();
	var checkcode = $("input[name=checkcode]").val();//验证码
	var remenber = $("[name=yhxy]:checked");//记住用户名
	var rem_val="";
    if (remenber.length>0){
    	rem_val="1";
    }

	$.ajax({
		url:"index" ,
		data:{'module':'login','name':'dologin','username':username,'password':password,'checkcode':checkcode,'remenber':rem_val},
		type:"POST",
		dataType:'json',
		success:function(data){
			if(data.R == '-1'){
				layer.alert('登陆失败,用户名或密码错误');
			}else if(data.R == '-2'){
				layer.alert("验证码错误");
				refreshnum();
			}else if(data.R == '1'){
				window.location = 'index';
			}
		}
	});	
}

//注册
function reg(){
	//var ishk = $("select[name=ishk]").val();
	var username = $("input[name=reg_username]").val();
	var company = $("input[name=reg_company]").val();
	var password = $("input[name=reg_password]").val();
	var repass = $("input[name=repass]").val();
	var yhxy = $("[name=yhxy]:checked");//用户协议
	var mobile = $("input[name=reg_mobile]").val();
	var email = $("input[name=reg_email]").val();
	var yzm = $("input[name=yzm]").val();
	if(!checkEmail(email)){
		layer.alert("请输入正确的电子邮箱");
		return false;
	}
	ishk = '1';
	if(ishk=='1'){
		if (mobile==""||!mobile.match(/^(0|86|17951)?(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$/))
		{
			layer.alert("请输入正确的手机号码");
			return false;
		}
	}
	/*if(ishk=='2'){
		if(username==""||!username.match(/^(00852|852)?(5[1-6]|5[9]|6[0-9]|8[0-9]|9[0-8]){6}$/)){
			layer.alert("请输入正确的香港手机号码");
			return false;
		}
	}*/
	/*if(company == ''){
		layer.alert("请输入公司名称");
		return false;
	}*/
	if(password == ''){
		layer.alert("请输入密码");
		return false;
	}
	if (password.length < 6)
	{
		layer.alert("密码至少6个字符");
		return false;
	}
	var hasNumber = false;
	var hasUpper = false;
	for(var i =0;i<password.length;i++){
		var s =  password[i];
		if(s.match(/^\d+$/)){
			hasNumber = true;
		}
		if(s.charCodeAt() >= 65 && s.charCodeAt() <= 90){
			hasUpper = true;
		}
	}
	if (!hasNumber)
	{
		layer.alert("密码必须含有一个数字");
		return false;
	}
	if (!hasUpper)
	{
		layer.alert("密码必须含有一个大写字母");
		return false;
	}
	if(password!=repass){
		layer.alert("两次输入的密码不一致");
		return false;
	}

    checkSjyz(email,yzm,3)
    if(isTrue3==0){
        layer.alert('验证码错误');
        return false;
    }

    if (yhxy.length<=0){
    	layer.alert("请阅读并同意创意电子有限公司用户注册协议");
    	return false;
    }

	$.ajax({
		url:"index",
		data:{'module':'login','name':'doreg','username':username,'password':password,'email':email,'company':company , 'mobile':mobile},
		type:"POST",
		dataType:'json',
		success:function(data){
			regUserCallback(data.R , email);
		}
	});
}

function reg_vali(email){
	if(!checkEmail(email)){
		layer.alert("请输入正确的电子邮箱");
		return false;
	}else{
		$.ajax({
			url:'index?module=login&name=reg_vali&email='+email,
			async:false,
			dataType:'json',
			success:function(res){
                //layer.alert('邮件发送成功，请注意查收!');
                layer.alert(res.msg);
                return false;
			}
		});
	}

}

function regUserCallback(result , username){
	function GetRequest() {
 		var url = location.search; //获取url中"?"符后的字串
   		var theRequest = new Object();
	    if (url.indexOf("?") != -1) {
		   var str = url.substr(1);
		   strs = str.split("&");
		   for(var i = 0; i < strs.length; i ++) {
			 theRequest[strs[i].split("=")[0]]=(strs[i].split("=")[1]);
		   }
	    }
	    return theRequest;
	}
	var Request = new Object();
	Request = GetRequest();
	backUrl=Request["backUrl"];
	if ( result == '1' ){
		if(backUrl!=undefined){
			window.location.href=decodeURIComponent(backUrl);
		}else{
			window.location.href="index";
		}
	}else if(result == '-2'){
		layer.alert("注册失败");
		return false;
	}else if(result == '-1'){
		layer.alert("账号"+username+"已存在");
		return false;
	}
}


//短信验证码校验
function checkSjyz(mobile,val,type){
	$.ajax({
		async:false, 
        url:"index",
        data:{
            'module':'login',
            'name':'checkSjyz',
            'mobile':mobile,
            'val':val,
            'type':type
        },
        dataType:'json',
        success:function(res){
            if(res.error == 0){
            	if(type==1){
            		isTrue=1;
            	}else if(type==2){
            		isTrue2=1;
            	}else{
            		isTrue3=1;
            	}
                return true;
            }else{
            	if(type==1){
            		isTrue=0;
            	}else if(type==2){
            		isTrue2=0;
            	}else{
            		isTrue3=0;
            	}
                return false;
            }
        }
    });
}

//获取短信验证码
function sjyz(mobile,type){
    var ishk=$("[name=ishk]").val();
	if(ishk=='1'){
		if (mobile==""||!mobile.match(/^(0|86|17951)?(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$/))
		{
			layer.alert("请输入正确的大陆手机号码");
			return false;
		}
	}
	if(ishk=='2'){
		if(mobile==""||!mobile.match(/^(00852|852)?(5[1-6]|5[9]|6[0-9]|8[0-9]|9[0-8]){6}$/)){
			layer.alert("请输入正确的香港手机号码");
			return false;
		}
	}
    $.ajax({
        url:"index",
        data:{
            'module':'login',
            'name':'sjyz',
            'mobile':mobile,
            'type':type
        },
        dataType:'json',
        success:function(res){
            if(res.error == 0){
                var obj=$(".btn_sjyz");
                obj.attr("disabled",true);
                setTimeout(function(){
                    obj.attr("disabled",false);
                },1800000);
                layer.alert(res.msg);
                return false;
            }else{
                layer.alert(res.msg);
                return false;
            }
        }
    });
}


$(function(){
    //判断是否存在该Cookie，存在则不执行，否则执行
    if(getCookie("remenber@iecshop")!=null&&getCookie("remenber@iecshop")!=""){
        //alert(getCookie("rps@hcrm"));
        var info=eval(getCookie("remenber@iecshop"))
        $("[name=yhxy]").attr("checked",true);
        $("[name=login_username]").val(info);
    }
});

//读取Cookie
function getCookie(name){ 
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
    if(arr=document.cookie.match(reg)){
        return unescape(arr[2]); 
    }else {
        return null; 
    }
} 

//删除Cookie
function delCookie(name){ 
    var exp = new Date(); 
    exp.setTime(exp.getTime() - 1); 
    var cval=getCookie(name); 
    if(cval!=null){
        document.cookie= name + "="+cval+";expires="+exp.toGMTString(); 
    }
} 

//设置Cookie
//这是有设定过期时间的使用示例： 
//s20是代表20秒 
//h是指小时，如12小时则是：h12 
//d是天数，30天则：d30 
//setCookie("name","hayden","s20");
function setCookie(name,value,time){ 
    var strsec = getsec(time); 
    var exp = new Date(); 
    exp.setTime(exp.getTime() + strsec*1); 
    document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString(); 
} 

function getsec(str){ 
   //alert(str); 
   var str1=str.substring(1,str.length)*1; 
   var str2=str.substring(0,1); 
   if (str2=="s"){ 
        return str1*1000; 
   }else if (str2=="h"){ 
       return str1*60*60*1000; 
   }else if (str2=="d"){ 
       return str1*24*60*60*1000; 
   } 
} 

//清除提示
function clearRemark(){
	//$("div[name=username_remark]").html('');
	//$("div[name=password_remark]").html('');
	$("div[name=fail_remark]").html('');
}