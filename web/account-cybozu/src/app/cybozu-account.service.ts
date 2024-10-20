import { Injectable } from '@angular/core';
import { HttpClient } from "@angular/common/http";

const FUNCTION_DOMAIN:string = "https://asia-northeast1-tfounion-cfcb3.cloudfunctions.net";

@Injectable({
  providedIn: 'root'
})

export class CybozuAccountService {

  constructor(private http: HttpClient) { }

    /**
    * DBにサイボウアカウント情報を登録
    */
    async setCybozuAccount(gsuite_account, cybozu_id, cybozu_password):Promise<void> {

        try{
            const body: model = {
                gsuite_account : gsuite_account,
                cybozu_id      : cybozu_id,
                cybozu_password: cybozu_password
            };
            await this.http.post<helloResonse>(FUNCTION_DOMAIN + "/cybozu_account", JSON.stringify(body)).toPromise();

        } catch(e) {
            throw e;
        }
    }
}

interface helloResonse {
    Message: string
}

interface model {
    gsuite_account : string,
    cybozu_id      : string,
    cybozu_password: string
}
