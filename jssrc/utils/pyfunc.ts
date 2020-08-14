/**
 * Call python function defiend with `@JSCallableMethod`
 *
 * Example usage:
 *
 *    callPyFunc('test', 1, 2).then(ret => {
 *      // ret is test(1, 2) here
 *    })
 *
 * @param funcname Function defined in the addon
 * @param args List of parameters
 */
export function callPyFunc (
  funcname: string,
  ...args: any[]
): Promise<any> {
  return new Promise<any>((resolve, reject) => {
    const cmdstr = `pyfunc:${ADDON_UUID}:${funcname}:${JSON.stringify(args)}`
    pycmd(cmdstr, (ret) => {
      const error = ret.error as (string | null)
      if (error) return reject(new Error(error))
      else return resolve(ret.payload)
    })
  })
}
