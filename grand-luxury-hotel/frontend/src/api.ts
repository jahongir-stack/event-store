export const api=(import.meta.env.VITE_API_URL||"http://localhost:8000/api").replace(/\/$/,"");
export type RoomType={id:number;name:string;description:string;image_url:string;price_per_night:string;capacity:number;size_sqm:number;amenities:string;available_units?:number;stay_price?:string};
export type Booking={id:number;reference:string;room_type:string;check_in:string;check_out:string;guests:number;total:string;status:string;guest_name:string};
export const token=()=>sessionStorage.getItem("hotel_token");
export async function request<T>(path:string,opts:RequestInit={}):Promise<T>{
 const headers:Record<string,string>={"Content-Type":"application/json",...(opts.headers as Record<string,string>||{})};
 if(token())headers.Authorization="Token "+token();
 const response=await fetch(api+path,{...opts,headers});
 const body=await response.json().catch(()=>null);
 if(!response.ok)throw new Error(typeof body?.detail==="string"?body.detail:JSON.stringify(body||"Request failed"));
 return body as T;
}
