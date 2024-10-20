import { Component } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CybozuAccountService } from './cybozu-account.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

    // 定数
    title = 'account-cybozu';
    messages_normal_end   = '登録が完了しました。'
    messages_abnormal_end = '異常が発生しました。'

    // 登録データ
    gsuite_account : string;
    cybozu_id      : string;
    cybozu_password: string;

    // 処理状況
    isExecution: boolean = false;

    constructor(private snackBar: MatSnackBar, private service: CybozuAccountService) {
    }

    /**
    * 追加処理
    * @event 登録ボタンをクリックした時
    */
    async execProcess(){

        this.isExecution = true

        // 登録
        try {
            await this.service.setCybozuAccount(this.gsuite_account, this.cybozu_id, this.cybozu_password);

            // 完了メッセージを表示
            let snakbarRef = this.snackBar.open(this.messages_normal_end, "OK", { duration: 1000 ,horizontalPosition:"start" });

        }catch(e){
            console.log(e);
            this.snackBar.open(this.messages_abnormal_end, "Close", { duration: 1000});
        }

        this.isExecution = false
    }
}
