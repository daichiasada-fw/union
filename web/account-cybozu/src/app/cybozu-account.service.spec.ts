import { TestBed } from '@angular/core/testing';

import { CybozuAccountService } from './cybozu-account.service';

describe('CybozuAccountService', () => {
  let service: CybozuAccountService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CybozuAccountService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
